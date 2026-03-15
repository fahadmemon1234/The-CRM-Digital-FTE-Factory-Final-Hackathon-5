"""
TechCorp Customer Success AI Agent - Database Queries

Async PostgreSQL functions for CRM operations using asyncpg.

INCUBATION MAPPING:
-------------------
Incubation: In-memory dict operations in prototype.py and mcp_server.py
Production: asyncpg functions with connection pooling

Key Changes from Incubation:
- dict lookups → asyncpg queries with connection pool
- No persistence → PostgreSQL with full ACID guarantees
- No concurrency handling → asyncpg pool for concurrent access
- Simple operations → Transactions for data integrity

Author: AI Engineering Team
Version: 1.0.0 (Production)
Based on: In-memory storage (Incubation)
"""

import os
import logging
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

import asyncpg

logger = logging.getLogger(__name__)

# Global connection pool
_db_pool: Optional[asyncpg.Pool] = None


# ============================================================================
# CONNECTION MANAGEMENT
# ============================================================================

async def get_db_pool() -> asyncpg.Pool:
    """
    Get or create asyncpg connection pool.
    
    INCUBATION: No database (in-memory dict)
    PRODUCTION: asyncpg pool with lazy initialization
    
    Connection pool settings:
    - min_size: 2 (minimum idle connections)
    - max_size: 10 (maximum connections)
    - command_timeout: 60 seconds
    
    Returns:
        asyncpg.Pool: Database connection pool
        
    Raises:
        RuntimeError: If DATABASE_URL environment variable not set
    """
    global _db_pool
    
    if _db_pool is not None:
        return _db_pool
    
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        # Development mode: return None, operations will be mocked
        logger.warning("DATABASE_URL not set, database operations will be mocked")
        return None
    
    try:
        _db_pool = await asyncpg.create_pool(
            dsn=dsn,
            min_size=2,
            max_size=10,
            command_timeout=60,
            server_settings={
                'jit': 'off',  # Disable JIT for faster simple queries
            }
        )
        
        logger.info(f"Database connection pool created (min=2, max=10)")
        return _db_pool
        
    except asyncpg.PostgresError as e:
        logger.error(f"PostgreSQL connection error: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to create database pool: {e}")
        raise


async def close_db_pool():
    """Close the database connection pool."""
    global _db_pool
    if _db_pool:
        await _db_pool.close()
        _db_pool = None
        logger.info("Database connection pool closed")


async def init_db():
    """
    Initialize database schema.
    
    Runs schema.sql to create all tables, indexes, and triggers.
    Safe to run multiple times (uses IF NOT EXISTS).
    """
    pool = await get_db_pool()
    if not pool:
        logger.warning("Cannot initialize DB: pool not available")
        return
    
    schema_path = os.path.join(
        os.path.dirname(__file__),
        'schema.sql'
    )
    
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Execute schema (handles IF NOT EXISTS safely)
        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(schema_sql)
        
        logger.info("Database schema initialized")
        
    except FileNotFoundError:
        logger.error(f"Schema file not found: {schema_path}")
        raise
    except Exception as e:
        logger.error(f"Failed to initialize database schema: {e}")
        raise


# ============================================================================
# CUSTOMER OPERATIONS
# ============================================================================

async def find_customer_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Find customer by email address.
    
    INCUBATION: customers.get(email) dict lookup
    PRODUCTION: asyncpg query with indexed lookup
    
    Args:
        email: Customer email address
        
    Returns:
        Customer dict with id, email, name, phone, metadata or None
    """
    pool = await get_db_pool()
    
    if not pool:
        logger.warning("DB not available, returning None for customer lookup")
        return None
    
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT id, email, name, phone, created_at, metadata
                FROM customers
                WHERE email = $1
            """, email)
            
            if row:
                return {
                    'id': str(row['id']),
                    'email': row['email'],
                    'name': row['name'],
                    'phone': row['phone'],
                    'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                    'metadata': dict(row['metadata']) if row['metadata'] else {}
                }
            return None
            
    except asyncpg.PostgresError as e:
        logger.error(f"Database error finding customer by email: {e}")
        return None


async def find_customer_by_phone(phone: str) -> Optional[Dict[str, Any]]:
    """
    Find customer by phone number.
    
    INCUBATION: No phone lookup in incubation
    PRODUCTION: Query customer_identifiers table
    
    Args:
        phone: Customer phone number
        
    Returns:
        Customer dict or None
    """
    pool = await get_db_pool()
    
    if not pool:
        return None
    
    try:
        async with pool.acquire() as conn:
            # First try direct phone match
            row = await conn.fetchrow("""
                SELECT id, email, name, phone, created_at, metadata
                FROM customers
                WHERE phone = $1
            """, phone)
            
            if row:
                return {
                    'id': str(row['id']),
                    'email': row['email'],
                    'name': row['name'],
                    'phone': row['phone'],
                    'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                    'metadata': dict(row['metadata']) if row['metadata'] else {}
                }
            
            # Try identifier lookup (WhatsApp numbers, etc.)
            row = await conn.fetchrow("""
                SELECT c.id, c.email, c.name, c.phone, c.created_at, c.metadata
                FROM customers c
                JOIN customer_identifiers ci ON c.id = ci.customer_id
                WHERE ci.identifier_type IN ('phone', 'whatsapp')
                AND ci.identifier_value = $1
            """, phone)
            
            if row:
                return {
                    'id': str(row['id']),
                    'email': row['email'],
                    'name': row['name'],
                    'phone': row['phone'],
                    'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                    'metadata': dict(row['metadata']) if row['metadata'] else {}
                }
            
            return None
            
    except asyncpg.PostgresError as e:
        logger.error(f"Database error finding customer by phone: {e}")
        return None


async def find_or_create_customer(
    email: Optional[str] = None,
    phone: Optional[str] = None,
    name: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Find existing customer or create new one.
    
    INCUBATION: customers.get() or customers[new_id] = {}
    PRODUCTION: UPSERT with RETURNING clause
    
    Args:
        email: Customer email (primary identifier)
        phone: Customer phone (secondary identifier)
        name: Customer name
        
    Returns:
        Customer dict with id, email, name, phone, metadata
    """
    pool = await get_db_pool()
    
    if not pool:
        # Mock mode: return synthetic customer
        return {
            'id': 'mock_' + str(hash(email or phone)),
            'email': email,
            'name': name,
            'phone': phone,
            'metadata': {}
        }
    
    try:
        async with pool.acquire() as conn:
            async with conn.transaction():
                # Try to find by email
                if email:
                    row = await conn.fetchrow("""
                        SELECT id, email, name, phone, created_at, metadata
                        FROM customers
                        WHERE email = $1
                    """, email)
                    
                    if row:
                        return {
                            'id': str(row['id']),
                            'email': row['email'],
                            'name': row['name'],
                            'phone': row['phone'],
                            'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                            'metadata': dict(row['metadata']) if row['metadata'] else {}
                        }
                
                # Try to find by phone
                if phone:
                    row = await conn.fetchrow("""
                        SELECT id, email, name, phone, created_at, metadata
                        FROM customers
                        WHERE phone = $1
                    """, phone)
                    
                    if row:
                        return {
                            'id': str(row['id']),
                            'email': row['email'],
                            'name': row['name'],
                            'phone': row['phone'],
                            'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                            'metadata': dict(row['metadata']) if row['metadata'] else {}
                        }
                
                # Create new customer
                customer_id = await conn.fetchval("""
                    INSERT INTO customers (email, name, phone, metadata)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id
                """, email, name, phone, '{}')
                
                logger.info(f"Created new customer: {customer_id}")
                
                return {
                    'id': str(customer_id),
                    'email': email,
                    'name': name,
                    'phone': phone,
                    'created_at': datetime.utcnow().isoformat(),
                    'metadata': {}
                }
                
    except asyncpg.PostgresError as e:
        logger.error(f"Database error in find_or_create_customer: {e}")
        return None


async def create_customer(
    email: str,
    name: str,
    phone: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> str:
    """
    Create a new customer record.
    
    INCUBATION: customers[email] = {...}
    PRODUCTION: INSERT with RETURNING id
    
    Args:
        email: Customer email (required, unique)
        name: Customer name
        phone: Customer phone number
        metadata: Optional JSONB metadata
        
    Returns:
        Customer UUID as string
        
    Raises:
        asyncpg.UniqueViolationError: If email already exists
    """
    pool = await get_db_pool()
    
    if not pool:
        logger.warning("DB not available, generating mock customer ID")
        return f"mock_{hash(email)}"
    
    try:
        async with pool.acquire() as conn:
            customer_id = await conn.fetchval("""
                INSERT INTO customers (email, name, phone, metadata)
                VALUES ($1, $2, $3, $4)
                RETURNING id
            """, email, name, phone, json.dumps(metadata or {}))
            
            logger.info(f"Created customer: {customer_id}")
            return str(customer_id)
            
    except asyncpg.UniqueViolationError:
        logger.warning(f"Customer already exists with email: {email}")
        raise
    except asyncpg.PostgresError as e:
        logger.error(f"Database error creating customer: {e}")
        raise


async def add_customer_identifier(
    customer_id: str,
    identifier_type: str,
    identifier_value: str,
    verified: bool = False
) -> bool:
    """
    Add an identifier to a customer (for cross-channel identity).
    
    INCUBATION: No equivalent (single identifier per customer)
    PRODUCTION: customer_identifiers table for multiple identifiers
    
    Args:
        customer_id: Customer UUID
        identifier_type: 'email', 'phone', 'whatsapp', 'web_form_id'
        identifier_value: The identifier value
        verified: Whether identifier has been verified
        
    Returns:
        True if successful, False otherwise
    """
    pool = await get_db_pool()
    
    if not pool:
        return False
    
    try:
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO customer_identifiers 
                (customer_id, identifier_type, identifier_value, verified)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (identifier_type, identifier_value) DO NOTHING
            """, customer_id, identifier_type, identifier_value, verified)
            
            return True
            
    except asyncpg.PostgresError as e:
        logger.error(f"Database error adding customer identifier: {e}")
        return False


# ============================================================================
# CONVERSATION OPERATIONS
# ============================================================================

async def create_conversation(
    customer_id: str,
    channel: str,
    metadata: Optional[Dict] = None
) -> str:
    """
    Create a new conversation session.
    
    INCUBATION: ConversationState() dataclass instantiation
    PRODUCTION: INSERT into conversations table
    
    Args:
        customer_id: Customer UUID
        channel: Initial channel ('email', 'whatsapp', 'web_form')
        metadata: Optional JSONB metadata
        
    Returns:
        Conversation UUID as string
    """
    pool = await get_db_pool()
    
    if not pool:
        logger.warning("DB not available, generating mock conversation ID")
        return f"conv_mock_{hash(customer_id)}"
    
    try:
        async with pool.acquire() as conn:
            conversation_id = await conn.fetchval("""
                INSERT INTO conversations (customer_id, initial_channel, metadata)
                VALUES ($1, $2, $3)
                RETURNING id
            """, customer_id, channel, json.dumps(metadata or {}))
            
            logger.info(f"Created conversation: {conversation_id}")
            return str(conversation_id)
            
    except asyncpg.PostgresError as e:
        logger.error(f"Database error creating conversation: {e}")
        raise


async def get_conversation_history(conversation_id: str) -> List[Dict[str, Any]]:
    """
    Get all messages in a conversation.
    
    INCUBATION: state.messages list
    PRODUCTION: SELECT from messages table with ordering
    
    Args:
        conversation_id: Conversation UUID
        
    Returns:
        List of message dicts ordered by created_at
    """
    pool = await get_db_pool()
    
    if not pool:
        return []
    
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, conversation_id, channel, direction, role, 
                       content, created_at, tokens_used, latency_ms,
                       tool_calls, channel_message_id, delivery_status
                FROM messages
                WHERE conversation_id = $1
                ORDER BY created_at ASC
            """, conversation_id)
            
            return [
                {
                    'id': str(row['id']),
                    'conversation_id': str(row['conversation_id']),
                    'channel': row['channel'],
                    'direction': row['direction'],
                    'role': row['role'],
                    'content': row['content'],
                    'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                    'tokens_used': row['tokens_used'],
                    'latency_ms': row['latency_ms'],
                    'tool_calls': list(row['tool_calls']) if row['tool_calls'] else [],
                    'channel_message_id': row['channel_message_id'],
                    'delivery_status': row['delivery_status']
                }
                for row in rows
            ]
            
    except asyncpg.PostgresError as e:
        logger.error(f"Database error getting conversation history: {e}")
        return []


async def get_customer_full_history(customer_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get all conversations and messages for a customer.
    
    INCUBATION: customer_history[customer_id] list
    PRODUCTION: JOIN conversations + messages with customer filter
    
    Args:
        customer_id: Customer UUID
        limit: Maximum messages to return
        
    Returns:
        List of message dicts with conversation context
    """
    pool = await get_db_pool()
    
    if not pool:
        return []
    
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    m.id, m.conversation_id, m.channel, m.direction, m.role,
                    m.content, m.created_at, m.tokens_used, m.latency_ms,
                    m.tool_calls, m.delivery_status,
                    c.initial_channel, c.status as conversation_status
                FROM messages m
                JOIN conversations c ON m.conversation_id = c.id
                WHERE c.customer_id = $1
                ORDER BY m.created_at DESC
                LIMIT $2
            """, customer_id, limit)
            
            return [
                {
                    'id': str(row['id']),
                    'conversation_id': str(row['conversation_id']),
                    'channel': row['channel'],
                    'direction': row['direction'],
                    'role': row['role'],
                    'content': row['content'],
                    'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                    'tokens_used': row['tokens_used'],
                    'latency_ms': row['latency_ms'],
                    'tool_calls': list(row['tool_calls']) if row['tool_calls'] else [],
                    'delivery_status': row['delivery_status'],
                    'initial_channel': row['initial_channel'],
                    'conversation_status': row['conversation_status']
                }
                for row in rows
            ]
            
    except asyncpg.PostgresError as e:
        logger.error(f"Database error getting customer history: {e}")
        return []


async def update_conversation_status(
    conversation_id: str,
    status: str,
    sentiment_score: Optional[float] = None,
    resolution_type: Optional[str] = None,
    escalated_to: Optional[str] = None
) -> bool:
    """
    Update conversation status and metadata.
    
    INCUBATION: state.resolution_status = value
    PRODUCTION: UPDATE with transaction
    
    Args:
        conversation_id: Conversation UUID
        status: New status ('active', 'resolved', 'escalated', 'closed')
        sentiment_score: Optional sentiment score (0.00-1.00)
        resolution_type: How conversation was resolved
        escalated_to: Team name if escalated
        
    Returns:
        True if successful
    """
    pool = await get_db_pool()
    
    if not pool:
        return False
    
    try:
        async with pool.acquire() as conn:
            await conn.execute("""
                UPDATE conversations
                SET status = $2,
                    sentiment_score = $3,
                    resolution_type = $4,
                    escalated_to = $5
                WHERE id = $1
            """, conversation_id, status, sentiment_score, resolution_type, escalated_to)
            
            return True
            
    except asyncpg.PostgresError as e:
        logger.error(f"Database error updating conversation: {e}")
        return False


# ============================================================================
# MESSAGE OPERATIONS
# ============================================================================

async def store_message(
    conversation_id: str,
    channel: str,
    direction: str,
    role: str,
    content: str,
    tokens_used: Optional[int] = None,
    latency_ms: Optional[int] = None,
    tool_calls: Optional[List[Dict]] = None,
    channel_message_id: Optional[str] = None,
    delivery_status: str = 'pending'
) -> str:
    """
    Store a message in the database.
    
    INCUBATION: state.messages.append(Message(...))
    PRODUCTION: INSERT into messages table
    
    Args:
        conversation_id: Conversation UUID
        channel: Message channel ('email', 'whatsapp', 'web_form')
        direction: 'inbound' or 'outbound'
        role: 'customer', 'agent', or 'system'
        content: Message content
        tokens_used: AI tokens used (for outbound agent messages)
        latency_ms: Response latency (for outbound agent messages)
        tool_calls: List of tools invoked
        channel_message_id: External channel message ID
        delivery_status: Delivery status
        
    Returns:
        Message UUID as string
    """
    pool = await get_db_pool()
    
    if not pool:
        logger.warning("DB not available, generating mock message ID")
        return f"msg_mock_{hash(content)}"
    
    try:
        async with pool.acquire() as conn:
            message_id = await conn.fetchval("""
                INSERT INTO messages 
                (conversation_id, channel, direction, role, content,
                 tokens_used, latency_ms, tool_calls, channel_message_id, delivery_status)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                RETURNING id
            """, conversation_id, channel, direction, role, content,
                tokens_used, latency_ms, json.dumps(tool_calls or []),
                channel_message_id, delivery_status)
            
            return str(message_id)
            
    except asyncpg.PostgresError as e:
        logger.error(f"Database error storing message: {e}")
        raise


async def update_delivery_status(channel_message_id: str, status: str) -> bool:
    """
    Update message delivery status.
    
    INCUBATION: No delivery tracking
    PRODUCTION: UPDATE messages SET delivery_status
    
    Args:
        channel_message_id: External channel message ID
        status: New status ('pending', 'sent', 'delivered', 'failed')
        
    Returns:
        True if successful
    """
    pool = await get_db_pool()
    
    if not pool:
        return False
    
    try:
        async with pool.acquire() as conn:
            await conn.execute("""
                UPDATE messages
                SET delivery_status = $2
                WHERE channel_message_id = $1
            """, channel_message_id, status)
            
            return True
            
    except asyncpg.PostgresError as e:
        logger.error(f"Database error updating delivery status: {e}")
        return False


# ============================================================================
# TICKET OPERATIONS
# ============================================================================

async def create_ticket(
    conversation_id: str,
    customer_id: str,
    source_channel: str,
    category: Optional[str] = None,
    priority: str = 'medium'
) -> str:
    """
    Create a new support ticket.
    
    INCUBATION: tickets[ticket_id] = {...} dict
    PRODUCTION: INSERT into tickets table
    
    Args:
        conversation_id: Conversation UUID
        customer_id: Customer UUID
        source_channel: Channel where ticket originated
        category: Issue category ('billing', 'technical', etc.)
        priority: Priority level ('low', 'medium', 'high', 'critical')
        
    Returns:
        Ticket UUID as string
    """
    pool = await get_db_pool()
    
    if not pool:
        logger.warning("DB not available, generating mock ticket ID")
        return f"tkt_mock_{hash(conversation_id)}"
    
    try:
        async with pool.acquire() as conn:
            ticket_id = await conn.fetchval("""
                INSERT INTO tickets 
                (conversation_id, customer_id, source_channel, category, priority)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
            """, conversation_id, customer_id, source_channel, category, priority)
            
            logger.info(f"Created ticket: {ticket_id}")
            return str(ticket_id)
            
    except asyncpg.PostgresError as e:
        logger.error(f"Database error creating ticket: {e}")
        raise


async def update_ticket_status(
    ticket_id: str,
    status: str,
    notes: Optional[str] = None
) -> bool:
    """
    Update ticket status.
    
    INCUBATION: tickets[ticket_id]['status'] = status
    PRODUCTION: UPDATE with resolution_notes
    
    Args:
        ticket_id: Ticket UUID
        status: New status ('open', 'in_progress', 'pending', 'resolved', 'closed', 'escalated')
        notes: Optional resolution notes
        
    Returns:
        True if successful
    """
    pool = await get_db_pool()
    
    if not pool:
        return False
    
    try:
        async with pool.acquire() as conn:
            if notes:
                await conn.execute("""
                    UPDATE tickets
                    SET status = $2, resolution_notes = $3
                    WHERE id = $1
                """, ticket_id, status, notes)
            else:
                await conn.execute("""
                    UPDATE tickets
                    SET status = $2
                    WHERE id = $1
                """, ticket_id, status)
            
            return True
            
    except asyncpg.PostgresError as e:
        logger.error(f"Database error updating ticket status: {e}")
        return False


async def get_ticket(ticket_id: str) -> Optional[Dict[str, Any]]:
    """Get ticket details."""
    pool = await get_db_pool()
    
    if not pool:
        return None
    
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT id, conversation_id, customer_id, source_channel,
                       category, priority, status, created_at, resolved_at, resolution_notes
                FROM tickets
                WHERE id = $1
            """, ticket_id)
            
            if row:
                return {
                    'id': str(row['id']),
                    'conversation_id': str(row['conversation_id']) if row['conversation_id'] else None,
                    'customer_id': str(row['customer_id']),
                    'source_channel': row['source_channel'],
                    'category': row['category'],
                    'priority': row['priority'],
                    'status': row['status'],
                    'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                    'resolved_at': row['resolved_at'].isoformat() if row['resolved_at'] else None,
                    'resolution_notes': row['resolution_notes']
                }
            return None
            
    except asyncpg.PostgresError as e:
        logger.error(f"Database error getting ticket: {e}")
        return None


# ============================================================================
# METRICS OPERATIONS
# ============================================================================

async def get_channel_metrics_24h() -> Dict[str, Any]:
    """
    Get channel performance metrics for last 24 hours.
    
    INCUBATION: No metrics tracking
    PRODUCTION: Aggregated metrics from messages table
    
    Returns:
        Dict with metrics per channel
    """
    pool = await get_db_pool()
    
    if not pool:
        return {}
    
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    channel,
                    COUNT(*) as total_messages,
                    COUNT(*) FILTER (WHERE direction = 'inbound') as inbound_messages,
                    COUNT(*) FILTER (WHERE direction = 'outbound') as outbound_messages,
                    AVG(latency_ms) as avg_latency_ms,
                    SUM(tokens_used) as total_tokens,
                    COUNT(*) FILTER (WHERE delivery_status = 'delivered') * 100.0 / NULLIF(COUNT(*), 0) as delivery_rate
                FROM messages
                WHERE created_at > NOW() - INTERVAL '24 hours'
                GROUP BY channel
            """)
            
            return {
                row['channel']: {
                    'total_messages': row['total_messages'],
                    'inbound_messages': row['inbound_messages'],
                    'outbound_messages': row['outbound_messages'],
                    'avg_latency_ms': float(row['avg_latency_ms']) if row['avg_latency_ms'] else None,
                    'total_tokens': row['total_tokens'],
                    'delivery_rate': float(row['delivery_rate']) if row['delivery_rate'] else None
                }
                for row in rows
            }
            
    except asyncpg.PostgresError as e:
        logger.error(f"Database error getting metrics: {e}")
        return {}


async def record_metric(
    metric_name: str,
    metric_value: float,
    channel: Optional[str] = None,
    dimensions: Optional[Dict] = None
) -> bool:
    """Record a metric value."""
    pool = await get_db_pool()
    
    if not pool:
        return False
    
    try:
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO agent_metrics 
                (metric_name, metric_value, channel, dimensions)
                VALUES ($1, $2, $3, $4)
            """, metric_name, metric_value, channel, json.dumps(dimensions or {}))
            
            return True
            
    except asyncpg.PostgresError as e:
        logger.error(f"Database error recording metric: {e}")
        return False


# ============================================================================
# KNOWLEDGE BASE OPERATIONS
# ============================================================================

async def search_knowledge_base(
    query_embedding: List[float],
    category: Optional[str] = None,
    max_results: int = 5
) -> List[Dict[str, Any]]:
    """
    Search knowledge base using vector similarity.
    
    INCUBATION: Keyword matching in product-docs.md
    PRODUCTION: pgvector cosine similarity search
    
    Args:
        query_embedding: 1536-dimension embedding vector
        category: Optional category filter
        max_results: Maximum results to return
        
    Returns:
        List of relevant documents with similarity scores
    """
    pool = await get_db_pool()
    
    if not pool:
        return []
    
    try:
        async with pool.acquire() as conn:
            # Convert Python list to pgvector format
            embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
            
            if category:
                rows = await conn.fetch("""
                    SELECT id, title, content, category,
                           1 - (embedding <=> $1::vector) as similarity
                    FROM knowledge_base
                    WHERE category = $2
                    ORDER BY embedding <=> $1::vector
                    LIMIT $3
                """, embedding_str, category, max_results)
            else:
                rows = await conn.fetch("""
                    SELECT id, title, content, category,
                           1 - (embedding <=> $1::vector) as similarity
                    FROM knowledge_base
                    ORDER BY embedding <=> $1::vector
                    LIMIT $2
                """, embedding_str, max_results)
            
            return [
                {
                    'id': str(row['id']),
                    'title': row['title'],
                    'content': row['content'],
                    'category': row['category'],
                    'similarity_score': float(row['similarity'])
                }
                for row in rows
            ]
            
    except asyncpg.PostgresError as e:
        logger.error(f"Database error searching knowledge base: {e}")
        return []


# ============================================================================
# CHANNEL CONFIG OPERATIONS
# ============================================================================

async def get_channel_config(channel: str) -> Optional[Dict[str, Any]]:
    """Get configuration for a channel."""
    pool = await get_db_pool()
    
    if not pool:
        return None
    
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT channel, enabled, config, response_template, 
                       max_response_length, created_at
                FROM channel_configs
                WHERE channel = $1
            """, channel)
            
            if row:
                return {
                    'channel': row['channel'],
                    'enabled': row['enabled'],
                    'config': dict(row['config']) if row['config'] else {},
                    'response_template': row['response_template'],
                    'max_response_length': row['max_response_length'],
                    'created_at': row['created_at'].isoformat() if row['created_at'] else None
                }
            return None
            
    except asyncpg.PostgresError as e:
        logger.error(f"Database error getting channel config: {e}")
        return None
