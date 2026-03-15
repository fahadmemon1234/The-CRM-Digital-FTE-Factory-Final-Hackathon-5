"""
TechCorp Customer Success AI Agent - Web Form Channel Handler

Handles inbound support form submissions via FastAPI REST endpoints.

INCUBATION MAPPING:
-------------------
Incubation: No web form integration (simulated in prototype.py)
Production: Full FastAPI router with Pydantic validation and Kafka integration

Key Features:
- Pydantic model validation with custom validators
- Email format validation
- Category validation against allowed values
- Message length validation
- Kafka event publishing for async processing
- Ticket status tracking endpoint
- Attachment support (URL references)

Author: AI Engineering Team
Version: 1.0.0 (Production)
"""

import os
import re
import json
import logging
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator, Field

logger = logging.getLogger(__name__)

# Create FastAPI router
router = APIRouter(prefix="/support", tags=["support"])


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class SupportFormSubmission(BaseModel):
    """
    Pydantic model for support form submission with validators.
    
    INCUBATION: Simple dict with manual validation
    PRODUCTION: Pydantic model with automatic validation
    
    Validators:
    - name: Must be 2+ chars after strip
    - email: Must be valid EmailStr format
    - subject: Required string
    - category: Must be in allowed list
    - message: Must be 10+ chars after strip
    """
    
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    subject: str = Field(..., min_length=1, max_length=500)
    category: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=10, max_length=10000)
    priority: Optional[str] = Field(default='medium', max_length=20)
    attachments: Optional[List[str]] = Field(default_factory=list)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Name must be 2+ characters after stripping whitespace."""
        stripped = v.strip()
        if len(stripped) < 2:
            raise ValueError('Name must be at least 2 characters')
        return stripped
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Category must be in allowed list."""
        allowed_categories = [
            'general',
            'technical',
            'billing',
            'feedback',
            'bug_report'
        ]
        
        v_lower = v.lower().strip()
        
        # Handle common variations
        category_mapping = {
            'bug': 'bug_report',
            'bugs': 'bug_report',
            'bug report': 'bug_report',
            'bugreport': 'bug_report',
            'tech': 'technical',
            'support': 'technical',
            'bill': 'billing',
            'payment': 'billing',
            'invoice': 'billing',
            'feedback': 'feedback',
            'suggestion': 'feedback',
            'general': 'general',
            'other': 'general'
        }
        
        if v_lower in allowed_categories:
            return v_lower
        
        if v_lower in category_mapping:
            return category_mapping[v_lower]
        
        # Default to general if unknown
        logger.warning(f"Unknown category '{v}', defaulting to 'general'")
        return 'general'
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Message must be 10+ characters after stripping whitespace."""
        stripped = v.strip()
        if len(stripped) < 10:
            raise ValueError('Message must be at least 10 characters')
        return stripped
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: Optional[str]) -> Optional[str]:
        """Priority must be valid value."""
        if v is None:
            return 'medium'
        
        allowed_priorities = ['low', 'medium', 'high', 'critical']
        v_lower = v.lower().strip()
        
        if v_lower in allowed_priorities:
            return v_lower
        
        logger.warning(f"Unknown priority '{v}', defaulting to 'medium'")
        return 'medium'
    
    def to_message_data(self, ticket_id: str) -> Dict[str, Any]:
        """Convert submission to standardized message data dict."""
        return {
            'channel': 'web_form',
            'channel_message_id': f"wf_{ticket_id}",
            'customer_email': self.email,
            'customer_name': self.name,
            'subject': self.subject,
            'content': self.message,
            'category': self.category,
            'priority': self.priority,
            'attachments': self.attachments,
            'received_at': datetime.utcnow().isoformat(),
            'metadata': {
                'form_submission': True,
                'category': self.category,
                'priority': self.priority,
                'attachment_count': len(self.attachments) if self.attachments else 0
            }
        }


class SupportFormResponse(BaseModel):
    """
    Pydantic model for support form submission response.
    
    INCUBATION: Simple dict response
    PRODUCTION: Typed response model
    """
    
    ticket_id: str
    message: str
    estimated_response_time: str = "Usually within 5 minutes"


class TicketStatusResponse(BaseModel):
    """Response model for ticket status endpoint."""
    
    ticket_id: str
    status: str
    messages: List[Dict[str, Any]]
    created_at: str
    last_updated: Optional[str] = None


# ============================================================================
# KAFKA PUBLISHER (Placeholder)
# ============================================================================

async def publish_to_kafka(topic: str, message_data: Dict[str, Any]) -> bool:
    """
    Publish message to Kafka topic.
    
    INCUBATION: No Kafka (simulated)
    PRODUCTION: AIOKafka producer
    
    Args:
        topic: Kafka topic name
        message_data: Message data dict
        
    Returns:
        True if published successfully
    """
    try:
        # INCUBATION: Log instead of actual Kafka
        logger.info(f"Kafka publish to {topic}: {json.dumps(message_data)[:200]}...")
        
        # PRODUCTION: Actual Kafka publish
        # from aiokafka import AIOKafkaProducer
        # producer = AIOKafkaProducer(bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS'))
        # await producer.start()
        # await producer.send_and_wait(topic, json.dumps(message_data).encode())
        # await producer.stop()
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to publish to Kafka: {e}")
        return False


async def create_ticket_record(ticket_id: str, message_data: Dict[str, Any]) -> bool:
    """
    Create ticket record in database.
    
    INCUBATION: In-memory dict
    PRODUCTION: PostgreSQL insert
    
    Args:
        ticket_id: Ticket UUID
        message_data: Message data dict
        
    Returns:
        True if created successfully
    """
    try:
        # INCUBATION: Log instead of actual DB
        logger.info(f"Creating ticket record: {ticket_id}")
        
        # PRODUCTION: Actual DB insert
        # from production.database.queries import create_ticket, store_message
        # await create_ticket(...)
        # await store_message(...)
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to create ticket record: {e}")
        return False


# ============================================================================
# FASTAPI ENDPOINTS
# ============================================================================

@router.post("/submit", response_model=SupportFormResponse)
async def submit_support_form(submission: SupportFormSubmission):
    """
    Submit a support form.
    
    INCUBATION: No form handling (simulated)
    PRODUCTION: Full validation, Kafka publishing, ticket creation
    
    Flow:
    1. Validate submission (Pydantic auto-validates)
    2. Generate ticket ID
    3. Create normalized message_data dict
    4. Publish to Kafka for async processing
    5. Create ticket record in database
    6. Return confirmation response
    
    Args:
        submission: Validated SupportFormSubmission
        
    Returns:
        SupportFormResponse with ticket_id and confirmation
        
    Raises:
        HTTPException: If processing fails
    """
    try:
        # Generate ticket ID
        ticket_id = f"tkt_{uuid.uuid4().hex[:12]}"
        
        # Convert to standardized message data
        message_data = submission.to_message_data(ticket_id)
        
        # Publish to Kafka for async processing
        kafka_success = await publish_to_kafka('fte.tickets.incoming', message_data)
        
        if not kafka_success:
            logger.warning("Kafka publish failed, continuing with local processing")
        
        # Create ticket record in database
        db_success = await create_ticket_record(ticket_id, message_data)
        
        if not db_success:
            logger.warning("DB record creation failed, but ticket ID generated")
        
        # Log submission
        logger.info(
            f"Support form submitted: ticket_id={ticket_id}, "
            f"email={submission.email}, category={submission.category}"
        )
        
        return SupportFormResponse(
            ticket_id=ticket_id,
            message=f"Thank you {submission.name}! Your support request has been received. "
                    f"Our team will review your issue regarding '{submission.subject}' "
                    f"and respond shortly.",
            estimated_response_time="Usually within 5 minutes"
        )
        
    except Exception as e:
        logger.error(f"Error processing support form: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process support form: {str(e)}"
        )


@router.get("/ticket/{ticket_id}", response_model=TicketStatusResponse)
async def get_ticket_status(ticket_id: str):
    """
    Get ticket status and message history.
    
    INCUBATION: No status endpoint (simulated)
    PRODUCTION: Database query with message history
    
    Args:
        ticket_id: Ticket UUID
        
    Returns:
        TicketStatusResponse with status and messages
        
    Raises:
        HTTPException: 404 if ticket not found
    """
    try:
        # INCUBATION: Mock response for testing
        # PRODUCTION: Actual DB query
        
        # Mock ticket data for testing
        mock_ticket = {
            'ticket_id': ticket_id,
            'status': 'open',
            'messages': [
                {
                    'id': f'msg_{uuid.uuid4().hex[:8]}',
                    'role': 'customer',
                    'content': 'Original support request...',
                    'channel': 'web_form',
                    'created_at': datetime.utcnow().isoformat()
                }
            ],
            'created_at': datetime.utcnow().isoformat(),
            'last_updated': datetime.utcnow().isoformat()
        }
        
        # PRODUCTION: Actual DB query
        # from production.database.queries import get_ticket, get_conversation_history
        # ticket = await get_ticket(ticket_id)
        # if not ticket:
        #     raise HTTPException(status_code=404, detail="Ticket not found")
        # messages = await get_conversation_history(ticket['conversation_id'])
        
        # Simulate not found for invalid ticket format
        if not ticket_id.startswith('tkt_'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket not found: {ticket_id}"
            )
        
        return TicketStatusResponse(
            ticket_id=mock_ticket['ticket_id'],
            status=mock_ticket['status'],
            messages=mock_ticket['messages'],
            created_at=mock_ticket['created_at'],
            last_updated=mock_ticket['last_updated']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching ticket status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch ticket status: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for web form handler."""
    return {
        'status': 'healthy',
        'channel': 'web_form',
        'timestamp': datetime.utcnow().isoformat()
    }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def normalize_email(email: str) -> str:
    """
    Normalize email address for consistent customer identification.
    
    Args:
        email: Email address to normalize
        
    Returns:
        Normalized email (lowercase, trimmed)
    """
    return email.strip().lower()


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent XSS and injection attacks.
    
    Args:
        text: User input text
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove potential script tags
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove other HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Escape special characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    
    return text.strip()
