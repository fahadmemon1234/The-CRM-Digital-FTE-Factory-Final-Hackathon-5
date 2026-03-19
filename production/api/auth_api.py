"""
TechCorp Customer Success AI Agent - Authentication API

JWT-based authentication with 30-minute token expiry.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30

# Database pool
db_pool = None

def set_db_pool(pool):
    """Set database pool from main module"""
    global db_pool
    db_pool = pool

async def get_db_pool():
    """Get database pool"""
    return db_pool

# Security scheme
security = HTTPBearer()

# ============================================================================
# Pydantic Models
# ============================================================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    company: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: dict

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    company: Optional[str]
    role: str
    created_at: datetime

# ============================================================================
# Helper Functions
# ============================================================================

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise credentials_exception
    
    # Get user from database
    if db_pool is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
    
    async with db_pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT id, name, email, company, role, created_at FROM users WHERE id = $1",
            user_id
        )
    
    if not user:
        raise credentials_exception
    
    return {
        "id": str(user['id']),
        "name": user['name'],
        "email": user['email'],
        "company": user['company'],
        "role": user['role'],
        "created_at": user['created_at'].isoformat() if user['created_at'] else None
    }

# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/register")
async def register(request: RegisterRequest):
    """Register a new user"""
    if db_pool is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
    
    # Check if user already exists
    async with db_pool.acquire() as conn:
        existing_user = await conn.fetchrow(
            "SELECT id FROM users WHERE email = $1",
            request.email
        )
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user
        hashed_pw = hash_password(request.password)
        user_id = await conn.fetchval(
            """
            INSERT INTO users (name, email, password_hash, company, role)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
            """,
            request.name,
            request.email,
            hashed_pw,
            request.company,
            'user'  # Default role
        )
        
        # Get user details
        user = await conn.fetchrow(
            "SELECT id, name, email, company, role, created_at FROM users WHERE id = $1",
            user_id
        )
    
    # Create JWT token
    access_token = create_access_token(
        data={"sub": str(user_id)},
        expires_delta=timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": str(user['id']),
            "name": user['name'],
            "email": user['email'],
            "company": user['company'],
            "role": user['role'],
            "created_at": user['created_at'].isoformat() if user['created_at'] else None
        }
    }

@router.post("/login")
async def login(request: LoginRequest):
    """Login and get JWT token"""
    if db_pool is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
    
    # Get user from database
    async with db_pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT id, name, email, password_hash, company, created_at FROM users WHERE email = $1",
            request.email
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(request.password, user['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        user_id = user['id']
        user_data = {
            "id": str(user['id']),
            "name": user['name'],
            "email": user['email'],
            "company": user['company'],
            "role": user['role'],
            "created_at": user['created_at'].isoformat() if user['created_at'] else None
        }
    
    # Create JWT token
    access_token = create_access_token(
        data={"sub": str(user_id)},
        expires_delta=timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": TOKEN_EXPIRE_MINUTES * 60,
        "user": user_data
    }

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {"user": current_user}

@router.post("/refresh")
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """Refresh access token"""
    # Create new JWT token
    access_token = create_access_token(
        data={"sub": current_user['id']},
        expires_delta=timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/logout")
async def logout():
    """Logout (client should delete token)"""
    # In a real app, you might add token to a blacklist
    return {"message": "Successfully logged out"}
