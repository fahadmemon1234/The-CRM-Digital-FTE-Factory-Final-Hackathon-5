"""
TechCorp Customer Success AI Agent - Pytest Configuration and Fixtures

Shared fixtures and configuration for all production tests.

INCUBATION MAPPING:
-------------------
Incubation: No test fixtures (manual testing)
Production: Comprehensive pytest fixtures for async testing

Fixtures Provided:
- Async HTTP client for API testing
- Sample data for all channels
- Database mock fixtures
- Kafka mock fixtures

Author: AI Engineering Team
Version: 1.0.0 (Production)
"""

import os
import sys
import pytest
import asyncio
from datetime import datetime
from typing import AsyncGenerator, Dict, Any, Optional

import httpx


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

# Add production to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test configuration
BASE_URL = os.getenv("FTE_API_URL", "http://localhost:8000")
REQUEST_TIMEOUT = float(os.getenv("FTE_TEST_TIMEOUT", "30.0"))


# ============================================================================
# EVENT LOOP FIXTURE
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """
    Create an event loop for the test session.
    
    Required for pytest-asyncio to work properly.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# HTTP CLIENT FIXTURES
# ============================================================================

@pytest.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """
    Create an async HTTP client for API testing.
    
    INCUBATION: No HTTP client (manual testing)
    PRODUCTION: httpx.AsyncClient with base URL and timeout
    
    Yields:
        httpx.AsyncClient configured for the FTE API
    """
    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=httpx.Timeout(REQUEST_TIMEOUT)
    ) as client:
        yield client


@pytest.fixture
async def authenticated_client(client: httpx.AsyncClient) -> AsyncGenerator[httpx.AsyncClient, None]:
    """
    Create an authenticated async HTTP client.
    
    Add authentication headers for protected endpoints.
    
    Args:
        client: Base HTTP client fixture
        
    Yields:
        httpx.AsyncClient with authentication headers
    """
    # Add auth headers if available
    api_key = os.getenv("FTE_API_KEY")
    if api_key:
        client.headers["Authorization"] = f"Bearer {api_key}"
    
    yield client


# ============================================================================
# SAMPLE DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_webform_data() -> Dict[str, Any]:
    """
    Sample valid web form submission data.
    
    Returns:
        Dict with valid form fields
    """
    return {
        "name": "Test User",
        "email": "test@example.com",
        "subject": "Help with API",
        "category": "technical",
        "message": "I need help with the API authentication",
        "priority": "medium"
    }


@pytest.fixture
def sample_invalid_webform_data() -> Dict[str, Any]:
    """
    Sample invalid web form submission data.
    
    Returns:
        Dict with invalid form fields
    """
    return {
        "name": "A",  # Too short
        "email": "invalid-email",  # Invalid format
        "subject": "Hi",  # Too short
        "category": "invalid",  # Invalid category
        "message": "Short"  # Too short
    }


@pytest.fixture
def sample_gmail_webhook_data() -> Dict[str, Any]:
    """
    Sample Gmail Pub/Sub webhook notification.
    
    Returns:
        Dict with Pub/Sub message structure
    """
    import base64
    message_data = base64.b64encode(b"test notification").decode('utf-8')
    return {
        "message": {
            "data": message_data,
            "messageId": "test-123"
        },
        "subscription": "projects/test/subscriptions/gmail-push"
    }


@pytest.fixture
def sample_whatsapp_webhook_data() -> Dict[str, str]:
    """
    Sample WhatsApp (Twilio) webhook form data.
    
    Returns:
        Dict with Twilio webhook fields
    """
    return {
        "MessageSid": "SM123",
        "From": "whatsapp:+1234567890",
        "Body": "Hello, I need help",
        "ProfileName": "Test User"
    }


@pytest.fixture
def sample_customer_data() -> Dict[str, Any]:
    """
    Sample customer data for testing.
    
    Returns:
        Dict with customer fields
    """
    return {
        "email": "customer@example.com",
        "name": "Test Customer",
        "phone": "+1234567890"
    }


@pytest.fixture
def sample_conversation_data() -> Dict[str, Any]:
    """
    Sample conversation data for testing.
    
    Returns:
        Dict with conversation fields
    """
    return {
        "customer_id": "test-customer-id",
        "channel": "web_form",
        "messages": [
            {
                "role": "customer",
                "content": "Hello, I need help",
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "role": "agent",
                "content": "How can I help you?",
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
    }


# ============================================================================
# DATABASE MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_db_pool():
    """
    Create a mock asyncpg connection pool.
    
    INCUBATION: No database (in-memory dict)
    PRODUCTION: PostgreSQL with asyncpg pool
    
    This fixture mocks the pool to allow testing without
    an actual database connection.
    
    Yields:
        Mock database pool
    """
    from unittest.mock import AsyncMock, MagicMock
    
    pool = AsyncMock()
    
    # Mock fetchrow (single row query)
    pool.fetchrow = AsyncMock(return_value=None)
    
    # Mock fetch (multiple row query)
    pool.fetch = AsyncMock(return_value=[])
    
    # Mock execute (INSERT/UPDATE/DELETE)
    pool.execute = AsyncMock(return_value=None)
    
    # Mock transaction context manager
    transaction = AsyncMock()
    transaction.__aenter__ = AsyncMock(return_value=transaction)
    transaction.__aexit__ = AsyncMock(return_value=None)
    pool.transaction = MagicMock(return_value=transaction)
    
    yield pool


@pytest.fixture
def mock_get_db_pool(mock_db_pool):
    """
    Mock the get_db_pool function to return our mock pool.
    
    Usage:
        @pytest.mark.asyncio
        async def test_something(mock_get_db_pool):
            # get_db_pool() will return mock_db_pool
    """
    from unittest.mock import patch
    
    with patch('production.database.queries.get_db_pool', return_value=mock_db_pool):
        yield mock_db_pool


# ============================================================================
# KAFKA MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_kafka_producer():
    """
    Create a mock AIOKafka producer.
    
    INCUBATION: No event publishing
    PRODUCTION: Kafka events for escalations
    
    This fixture prevents actual Kafka connections during tests.
    
    Yields:
        Mock Kafka producer
    """
    from unittest.mock import AsyncMock
    
    producer = AsyncMock()
    producer.start = AsyncMock()
    producer.stop = AsyncMock()
    producer.send_and_wait = AsyncMock()
    
    yield producer


# ============================================================================
# CHANNEL HANDLER MOCKS
# ============================================================================

@pytest.fixture
def mock_gmail_handler():
    """Mock Gmail channel handler."""
    from unittest.mock import AsyncMock
    
    handler = AsyncMock()
    handler.send_reply = AsyncMock(return_value={"channel_message_id": "mock-123"})
    handler.process_notification = AsyncMock(return_value=[])
    
    yield handler


@pytest.fixture
def mock_whatsapp_handler():
    """Mock WhatsApp channel handler."""
    from unittest.mock import AsyncMock
    
    handler = AsyncMock()
    handler.send_message = AsyncMock(return_value={"channel_message_id": "SM-mock-123"})
    handler.process_webhook = AsyncMock(return_value={"channel": "whatsapp"})
    handler.validate_webhook = AsyncMock(return_value=True)
    
    yield handler


# ============================================================================
# AGENT MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_agent_response():
    """Mock AI agent response."""
    return {
        "response": "I can help you with that. Here's what you need to know...",
        "ticket_id": "tkt_mock_123",
        "escalated": False
    }


# ============================================================================
# UTILITY FIXTURES
# ============================================================================

@pytest.fixture
def mock_time():
    """Mock datetime to return consistent timestamps."""
    from unittest.mock import patch
    
    fixed_time = "2025-01-20T12:00:00Z"
    
    class MockDateTime:
        @classmethod
        def utcnow(cls):
            class MockDT:
                def isoformat(self):
                    return fixed_time
            return MockDT()
    
    with patch('datetime.datetime', MockDateTime):
        yield fixed_time


@pytest.fixture
def temp_test_dir(tmp_path):
    """
    Create a temporary test directory.
    
    Args:
        tmp_path: Pytest tmp_path fixture
        
    Yields:
        Path to temporary directory
    """
    yield tmp_path


# ============================================================================
# MARKERS
# ============================================================================

def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers",
        "e2e: mark test as end-to-end test requiring running services"
    )
    config.addinivalue_line(
        "markers",
        "integration: mark test as requiring external services (DB, Kafka)"
    )
    config.addinivalue_line(
        "markers",
        "unit: mark test as unit test with mocked dependencies"
    )
    config.addinivalue_line(
        "markers",
        "channel: mark test as channel-specific test"
    )
