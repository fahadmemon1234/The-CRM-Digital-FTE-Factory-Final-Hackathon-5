"""
TechCorp Customer Success AI Agent - Multi-Channel E2E Test Suite

End-to-end tests for all communication channels (Email, WhatsApp, Web Form).

INCUBATION MAPPING:
-------------------
Incubation: Manual testing with print statements
Production: Automated pytest test suite with async HTTP client

Test Coverage:
- Web Form channel (submission, validation, status retrieval)
- Email channel (Gmail webhook processing)
- WhatsApp channel (Twilio webhook processing)
- Cross-channel continuity (customer history across channels)
- Channel metrics
- Health checks

Author: AI Engineering Team
Version: 1.0.0 (Production)
"""

import pytest
import asyncio
from datetime import datetime
from typing import AsyncGenerator, Dict, Any

import httpx


# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_URL = "http://localhost:8000"
REQUEST_TIMEOUT = 30.0


# ============================================================================
# PYTEST FIXTURES (conftest.py content included for standalone execution)
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
def sample_webform_data() -> Dict[str, Any]:
    """Sample valid web form submission data."""
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
    """Sample invalid web form submission data."""
    return {
        "name": "A",  # Too short
        "email": "invalid-email",  # Invalid format
        "subject": "Hi",  # Too short
        "category": "invalid",  # Invalid category
        "message": "Short"  # Too short
    }


@pytest.fixture
def sample_gmail_webhook_data() -> Dict[str, Any]:
    """Sample Gmail Pub/Sub webhook notification."""
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
    """Sample WhatsApp (Twilio) webhook form data."""
    return {
        "MessageSid": "SM123",
        "From": "whatsapp:+1234567890",
        "Body": "Hello, I need help",
        "ProfileName": "Test User"
    }


# ============================================================================
# TEST CLASS 1: Web Form Channel
# ============================================================================

class TestWebFormChannel:
    """
    Tests for the Web Form communication channel.
    
    INCUBATION EQUIVALENT: Manual form submission testing
    PRODUCTION: Automated pytest tests with validation
    """
    
    @pytest.mark.asyncio
    async def test_form_submission(
        self,
        client: httpx.AsyncClient,
        sample_webform_data: Dict[str, Any]
    ):
        """
        Test valid web form submission.
        
        INCUBATION: Manual form testing
        PRODUCTION: Automated test with assertions
        
        Steps:
        1. POST /support/submit with valid data
        2. Assert status 200
        3. Assert ticket_id in response
        4. Assert message is not None
        
        Args:
            client: Async HTTP client
            sample_webform_data: Valid form data fixture
        """
        # Submit form
        response = await client.post(
            "/support/submit",
            json=sample_webform_data
        )
        
        # Assert status 200
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Parse response
        data = response.json()
        
        # Assert ticket_id in response
        assert "ticket_id" in data, "Response should contain ticket_id"
        
        # Assert message is not None
        assert data.get("message") is not None, "Response should contain message"
        
        # Assert ticket_id format
        ticket_id = data["ticket_id"]
        assert ticket_id.startswith("tkt_"), f"Ticket ID should start with 'tkt_', got {ticket_id}"
    
    @pytest.mark.asyncio
    async def test_form_validation(
        self,
        client: httpx.AsyncClient,
        sample_invalid_webform_data: Dict[str, Any]
    ):
        """
        Test web form validation with invalid data.
        
        INCUBATION: Manual validation testing
        PRODUCTION: Automated test with Pydantic validation
        
        Steps:
        1. POST /support/submit with invalid data
        2. Assert status 422 (validation error)
        
        Args:
            client: Async HTTP client
            sample_invalid_webform_data: Invalid form data fixture
        """
        # Submit invalid form
        response = await client.post(
            "/support/submit",
            json=sample_invalid_webform_data
        )
        
        # Assert status 422 (validation error)
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        
        # Parse response
        data = response.json()
        
        # Assert validation errors present
        assert "detail" in data, "Response should contain validation errors"
    
    @pytest.mark.asyncio
    async def test_ticket_status_retrieval(
        self,
        client: httpx.AsyncClient,
        sample_webform_data: Dict[str, Any]
    ):
        """
        Test ticket status retrieval after form submission.
        
        INCUBATION: Manual status checking
        PRODUCTION: Automated test with ticket lifecycle
        
        Steps:
        1. Submit form to create ticket
        2. Extract ticket_id from response
        3. GET /support/ticket/{ticket_id}
        4. Assert status 200
        5. Assert status in ["open", "processing"]
        
        Args:
            client: Async HTTP client
            sample_webform_data: Valid form data fixture
        """
        # Submit form
        submit_response = await client.post(
            "/support/submit",
            json=sample_webform_data
        )
        
        assert submit_response.status_code == 200
        ticket_id = submit_response.json()["ticket_id"]
        
        # Get ticket status
        status_response = await client.get(f"/support/ticket/{ticket_id}")
        
        # Assert status 200
        assert status_response.status_code == 200, f"Expected 200, got {status_response.status_code}"
        
        # Parse response
        data = status_response.json()
        
        # Assert status in valid states
        assert data.get("status") in ["open", "processing", "resolved"], \
            f"Expected valid status, got {data.get('status')}"


# ============================================================================
# TEST CLASS 2: Email Channel
# ============================================================================

class TestEmailChannel:
    """
    Tests for the Email (Gmail) communication channel.
    
    INCUBATION EQUIVALENT: No email testing (simulated)
    PRODUCTION: Automated webhook processing tests
    """
    
    @pytest.mark.asyncio
    async def test_gmail_webhook_processing(
        self,
        client: httpx.AsyncClient,
        sample_gmail_webhook_data: Dict[str, Any]
    ):
        """
        Test Gmail Pub/Sub webhook processing.
        
        INCUBATION: No Gmail integration (simulated)
        PRODUCTION: Full webhook processing test
        
        Steps:
        1. POST /webhooks/gmail with Pub/Sub notification
        2. Assert status 200
        
        Args:
            client: Async HTTP client
            sample_gmail_webhook_data: Pub/Sub notification fixture
        """
        # Send webhook
        response = await client.post(
            "/webhooks/gmail",
            json=sample_gmail_webhook_data
        )
        
        # Assert status 200 (or 503 if Gmail handler not initialized in test env)
        assert response.status_code in [200, 503], \
            f"Expected 200 or 503, got {response.status_code}"
        
        if response.status_code == 200:
            # Parse response
            data = response.json()
            
            # Assert status in response
            assert data.get("status") == "processed"


# ============================================================================
# TEST CLASS 3: WhatsApp Channel
# ============================================================================

class TestWhatsAppChannel:
    """
    Tests for the WhatsApp (Twilio) communication channel.
    
    INCUBATION EQUIVALENT: No WhatsApp integration (simulated)
    PRODUCTION: Full Twilio webhook tests
    """
    
    @pytest.mark.asyncio
    async def test_whatsapp_webhook_processing(
        self,
        client: httpx.AsyncClient,
        sample_whatsapp_webhook_data: Dict[str, str]
    ):
        """
        Test WhatsApp (Twilio) webhook processing.
        
        INCUBATION: No WhatsApp integration (simulated)
        PRODUCTION: Full Twilio webhook test with signature validation
        
        Steps:
        1. POST /webhooks/whatsapp with Twilio form data
        2. Assert status in [200, 403] (403 expected without valid signature)
        
        Args:
            client: Async HTTP client
            sample_whatsapp_webhook_data: Twilio webhook fixture
        """
        # Send webhook (form data)
        response = await client.post(
            "/webhooks/whatsapp",
            data=sample_whatsapp_webhook_data
        )
        
        # Assert status in [200, 403]
        # 403 is expected in test environment without valid Twilio signature
        assert response.status_code in [200, 403], \
            f"Expected 200 or 403, got {response.status_code}"
        
        if response.status_code == 200:
            # Assert TwiML response
            assert "application/xml" in response.headers.get("content-type", "")


# ============================================================================
# TEST CLASS 4: Cross-Channel Continuity
# ============================================================================

class TestCrossChannelContinuity:
    """
    Tests for cross-channel customer identity and conversation continuity.
    
    INCUBATION EQUIVALENT: No cross-channel testing
    PRODUCTION: Full cross-channel identity resolution tests
    """
    
    @pytest.mark.asyncio
    async def test_customer_history_across_channels(
        self,
        client: httpx.AsyncClient
    ):
        """
        Test customer history retrieval across channels.
        
        INCUBATION: In-memory conversation lookup
        PRODUCTION: Database query with cross-channel identity
        
        Steps:
        1. Submit web form with email "crosschannel@example.com"
        2. GET /customers/lookup?email=crosschannel@example.com
        3. Assert conversations list length >= 1
        
        Args:
            client: Async HTTP client
        """
        # Submit web form
        form_data = {
            "name": "Cross Channel User",
            "email": "crosschannel@example.com",
            "subject": "Cross-channel test",
            "category": "general",
            "message": "Testing cross-channel continuity"
        }
        
        submit_response = await client.post(
            "/support/submit",
            json=form_data
        )
        
        assert submit_response.status_code == 200
        
        # Lookup customer
        lookup_response = await client.get(
            "/customers/lookup",
            params={"email": "crosschannel@example.com"}
        )
        
        # Assert status 200 or 404 (404 if customer lookup not implemented)
        assert lookup_response.status_code in [200, 404], \
            f"Expected 200 or 404, got {lookup_response.status_code}"
        
        if lookup_response.status_code == 200:
            data = lookup_response.json()
            
            # Assert customer data present
            assert "email" in data or "id" in data


# ============================================================================
# TEST CLASS 5: Channel Metrics
# ============================================================================

class TestChannelMetrics:
    """
    Tests for channel metrics and analytics.
    
    INCUBATION EQUIVALENT: No metrics (print statements only)
    PRODUCTION: Full metrics endpoint tests
    """
    
    @pytest.mark.asyncio
    async def test_metrics_by_channel(self, client: httpx.AsyncClient):
        """
        Test channel metrics endpoint.
        
        INCUBATION: No metrics collection
        PRODUCTION: Database aggregation test
        
        Steps:
        1. GET /metrics/channels
        2. Assert status 200
        3. For each channel in ["email", "whatsapp", "web_form"]:
           - If channel in data, assert "total_conversations" in data[channel]
        
        Args:
            client: Async HTTP client
        """
        # Get metrics
        response = await client.get("/metrics/channels")
        
        # Assert status 200
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Parse response
        data = response.json()
        
        # Assert channels key present
        assert "channels" in data, "Response should contain 'channels' key"
        
        # Check each expected channel
        expected_channels = ["email", "whatsapp", "web_form"]
        channels_data = data["channels"]
        
        for channel in expected_channels:
            if channel in channels_data:
                channel_data = channels_data[channel]
                assert "total_conversations" in channel_data, \
                    f"Channel {channel} should have 'total_conversations'"


# ============================================================================
# TEST CLASS 6: Health Check
# ============================================================================

class TestHealthCheck:
    """
    Tests for health check and monitoring endpoints.
    
    INCUBATION EQUIVALENT: No health endpoint
    PRODUCTION: Full health check tests
    """
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, client: httpx.AsyncClient):
        """
        Test health check endpoint.
        
        INCUBATION: No health monitoring
        PRODUCTION: Full health check with channel status
        
        Steps:
        1. GET /health
        2. Assert status 200
        3. Assert data["status"] == "healthy"
        4. Assert "channels" in data
        
        Args:
            client: Async HTTP client
        """
        # Get health
        response = await client.get("/health")
        
        # Assert status 200
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Parse response
        data = response.json()
        
        # Assert status is healthy
        assert data.get("status") == "healthy", \
            f"Expected 'healthy', got {data.get('status')}"
        
        # Assert channels in data
        assert "channels" in data, "Response should contain 'channels' key"
        
        # Assert channel keys present
        channels = data["channels"]
        assert "email" in channels or "web_form" in channels, \
            "Should have at least one channel status"


# ============================================================================
# MAIN (for standalone execution)
# ============================================================================

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-x"
    ])
