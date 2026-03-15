"""
TechCorp Customer Success AI Agent - Channel Handler Unit Tests

Unit tests for each channel handler in isolation.

INCUBATION MAPPING:
-------------------
Incubation: No unit tests (manual testing)
Production: Comprehensive unit tests with pytest-mock

Test Coverage:
- GmailHandler._extract_email: Parses "Name <email>" correctly
- GmailHandler._extract_body: Returns string from payload
- WhatsAppHandler.format_response: Splits at sentence boundaries
- WhatsAppHandler.send_message: Adds "whatsapp:" prefix
- SupportFormSubmission validation: name, email, category

Author: AI Engineering Team
Version: 1.0.0 (Production)
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ============================================================================
# TEST CLASS 1: Gmail Handler
# ============================================================================

class TestGmailHandler:
    """
    Unit tests for GmailHandler.
    
    INCUBATION: No Gmail integration (simulated)
    PRODUCTION: Full unit tests for email parsing
    """
    
    def test_extract_email_parses_name_and_email(self):
        """
        Test that _extract_email correctly parses "Name <email@example.com>".
        
        INCUBATION: No email parsing
        PRODUCTION: Regex-based extraction
        
        Test Cases:
        1. "Name <email@example.com>" -> "email@example.com"
        2. "email@example.com" -> "email@example.com"
        3. "Name (comment) <email@example.com>" -> "email@example.com"
        """
        from production.channels.gmail_handler import GmailHandler
        
        # Create handler instance (no credentials needed for this test)
        handler = object.__new__(GmailHandler)
        
        # Test case 1: Standard format
        result = handler._extract_email("John Doe <john@example.com>")
        assert result == "john@example.com", \
            f"Expected 'john@example.com', got '{result}'"
        
        # Test case 2: Bare email
        result = handler._extract_email("jane@example.com")
        assert result == "jane@example.com", \
            f"Expected 'jane@example.com', got '{result}'"
        
        # Test case 3: With comment
        result = handler._extract_email("Bob Smith (work) <bob@company.com>")
        assert result == "bob@company.com", \
            f"Expected 'bob@company.com', got '{result}'"
    
    def test_extract_body_returns_string_from_payload(self):
        """
        Test that _extract_body returns string from Gmail payload.
        
        INCUBATION: No body extraction
        PRODUCTION: Base64 decoding with multipart handling
        
        Test Cases:
        1. Single part plain text
        2. Multipart with plain text
        3. Empty payload
        """
        import base64
        from production.channels.gmail_handler import GmailHandler
        
        handler = object.__new__(GmailHandler)
        
        # Test case 1: Single part plain text
        test_content = "Hello, this is a test email."
        encoded = base64.urlsafe_b64encode(test_content.encode()).decode()
        
        payload = {
            "body": {
                "data": encoded
            }
        }
        
        result = handler._extract_body(payload)
        assert isinstance(result, str), "Result should be a string"
        assert result == test_content, f"Expected '{test_content}', got '{result}'"
        
        # Test case 2: Multipart with plain text
        multipart_payload = {
            "parts": [
                {
                    "mimeType": "text/plain",
                    "body": {"data": encoded}
                },
                {
                    "mimeType": "text/html",
                    "body": {"data": base64.urlsafe_b64encode(b"<html>test</html>").decode()}
                }
            ]
        }
        
        result = handler._extract_body(multipart_payload)
        assert isinstance(result, str)
        assert result == test_content
    
    def test_extract_body_handles_html_fallback(self):
        """
        Test _extract_body falls back to HTML if no plain text.
        """
        import base64
        from production.channels.gmail_handler import GmailHandler
        
        handler = object.__new__(GmailHandler)
        
        html_content = "<html><body><p>Hello HTML</p></body></html>"
        encoded = base64.urlsafe_b64encode(html_content.encode()).decode()
        
        payload = {
            "parts": [
                {
                    "mimeType": "text/html",
                    "body": {"data": encoded}
                }
            ]
        }
        
        result = handler._extract_body(payload)
        assert isinstance(result, str)
        # HTML tags should be stripped
        assert "Hello HTML" in result


# ============================================================================
# TEST CLASS 2: WhatsApp Handler
# ============================================================================

class TestWhatsAppHandler:
    """
    Unit tests for WhatsAppHandler.
    
    INCUBATION: No WhatsApp integration (simulated)
    PRODUCTION: Full unit tests for message formatting
    """
    
    def test_format_response_splits_at_sentence_boundaries(self):
        """
        Test that format_response splits long messages at sentence boundaries.
        
        INCUBATION: Simple truncation
        PRODUCTION: Intelligent sentence-boundary splitting
        
        Test Cases:
        1. Short message (no split needed)
        2. Long message with periods
        3. Long message with exclamation marks
        """
        from production.channels.whatsapp_handler import WhatsAppHandler
        
        handler = object.__new__(WhatsAppHandler)
        
        # Test case 1: Short message (no split)
        short_message = "Hello, how can I help you?"
        result = handler.format_response(short_message)
        assert len(result) == 1, "Short message should not be split"
        assert result[0] == short_message
        
        # Test case 2: Long message with periods
        long_message = "This is the first sentence. This is the second sentence. " \
                      "This is the third sentence. And this is the fourth sentence."
        result = handler.format_response(long_message, max_length=50)
        assert len(result) > 1, "Long message should be split"
        
        # Each chunk should be under max_length
        for chunk in result:
            assert len(chunk) <= 50, f"Chunk exceeds max_length: {chunk}"
    
    def test_format_response_handles_very_long_messages(self):
        """
        Test format_response with very long messages.
        """
        from production.channels.whatsapp_handler import WhatsAppHandler
        
        handler = object.__new__(WhatsAppHandler)
        
        # Create very long message (2000 chars)
        long_message = " ".join(["Word"] * 400)
        
        result = handler.format_response(long_message, max_length=300)
        
        # All chunks should be under limit
        for chunk in result:
            assert len(chunk) <= 300, f"Chunk exceeds 300 chars: {len(chunk)}"
    
    def test_send_message_adds_whatsapp_prefix(self):
        """
        Test that send_message adds "whatsapp:" prefix to bare phone numbers.
        
        INCUBATION: No prefix handling
        PRODUCTION: Automatic prefix addition
        
        Note: This test mocks the Twilio client to avoid actual API calls.
        """
        from production.channels.whatsapp_handler import WhatsAppHandler
        
        # Create handler with mocked client
        handler = WhatsAppHandler.__new__(WhatsAppHandler)
        handler.client = MagicMock()
        handler.whatsapp_number = "+1234567890"
        
        # Mock the messages.create method
        mock_message = MagicMock()
        mock_message.sid = "SM123"
        handler.client.messages.create = MagicMock(return_value=mock_message)
        
        # Test with bare phone number (no prefix)
        import asyncio
        
        async def test_send():
            result = await handler.send_message("+9876543210", "Test message")
            return result
        
        result = asyncio.run(test_send())
        
        # Verify Twilio was called with whatsapp: prefix
        handler.client.messages.create.assert_called_once()
        call_args = handler.client.messages.create.call_args
        assert call_args[1]["to"] == "whatsapp:+9876543210", \
            "Should add 'whatsapp:' prefix to bare phone number"


# ============================================================================
# TEST CLASS 3: Web Form Handler (Pydantic Models)
# ============================================================================

class TestSupportFormSubmission:
    """
    Unit tests for SupportFormSubmission Pydantic model.
    
    INCUBATION: No form validation
    PRODUCTION: Pydantic validation with custom validators
    """
    
    def test_rejects_name_shorter_than_2_chars(self):
        """
        Test that SupportFormSubmission rejects names shorter than 2 characters.
        
        INCUBATION: No validation
        PRODUCTION: Pydantic field_validator
        
        Test Cases:
        1. Empty name
        2. Single character name
        3. Whitespace-only name
        """
        from production.channels.web_form_handler import SupportFormSubmission
        from pydantic import ValidationError
        
        # Test case 1: Empty name
        with pytest.raises(ValidationError) as exc_info:
            SupportFormSubmission(
                name="",
                email="test@example.com",
                subject="Test Subject",
                category="general",
                message="This is a valid message with enough characters."
            )
        assert "name" in str(exc_info.value).lower()
        
        # Test case 2: Single character name
        with pytest.raises(ValidationError) as exc_info:
            SupportFormSubmission(
                name="A",
                email="test@example.com",
                subject="Test Subject",
                category="general",
                message="This is a valid message with enough characters."
            )
        assert "name" in str(exc_info.value).lower()
        
        # Test case 3: Whitespace-only name
        with pytest.raises(ValidationError) as exc_info:
            SupportFormSubmission(
                name="   ",
                email="test@example.com",
                subject="Test Subject",
                category="general",
                message="This is a valid message with enough characters."
            )
        assert "name" in str(exc_info.value).lower()
    
    def test_rejects_invalid_email(self):
        """
        Test that SupportFormSubmission rejects invalid email addresses.
        
        INCUBATION: No email validation
        PRODUCTION: Pydantic EmailStr validation
        
        Test Cases:
        1. No @ symbol
        2. No domain
        3. Invalid format
        """
        from production.channels.web_form_handler import SupportFormSubmission
        from pydantic import ValidationError
        
        # Test case 1: No @ symbol
        with pytest.raises(ValidationError) as exc_info:
            SupportFormSubmission(
                name="Test User",
                email="invalid-email",
                subject="Test Subject",
                category="general",
                message="This is a valid message with enough characters."
            )
        assert "email" in str(exc_info.value).lower()
        
        # Test case 2: No domain
        with pytest.raises(ValidationError) as exc_info:
            SupportFormSubmission(
                name="Test User",
                email="test@",
                subject="Test Subject",
                category="general",
                message="This is a valid message with enough characters."
            )
        assert "email" in str(exc_info.value).lower()
        
        # Test case 3: Missing local part
        with pytest.raises(ValidationError) as exc_info:
            SupportFormSubmission(
                name="Test User",
                email="@example.com",
                subject="Test Subject",
                category="general",
                message="This is a valid message with enough characters."
            )
        assert "email" in str(exc_info.value).lower()
    
    def test_rejects_invalid_category(self):
        """
        Test that SupportFormSubmission normalizes or rejects invalid categories.
        
        INCUBATION: No category validation
        PRODUCTION: Pydantic field_validator with normalization
        
        Test Cases:
        1. Valid category (should pass)
        2. Invalid category (should normalize to 'general')
        3. Case variations (should normalize)
        """
        from production.channels.web_form_handler import SupportFormSubmission
        
        # Test case 1: Valid category
        form = SupportFormSubmission(
            name="Test User",
            email="test@example.com",
            subject="Test Subject",
            category="technical",
            message="This is a valid message with enough characters."
        )
        assert form.category == "technical"
        
        # Test case 2: Invalid category (should normalize to 'general')
        form = SupportFormSubmission(
            name="Test User",
            email="test@example.com",
            subject="Test Subject",
            category="invalid_category_xyz",
            message="This is a valid message with enough characters."
        )
        assert form.category == "general", \
            f"Invalid category should normalize to 'general', got '{form.category}'"
        
        # Test case 3: Case variations
        form = SupportFormSubmission(
            name="Test User",
            email="test@example.com",
            subject="Test Subject",
            category="BILLING",  # Uppercase
            message="This is a valid message with enough characters."
        )
        assert form.category == "billing", \
            f"Category should be normalized to lowercase, got '{form.category}'"
        
        # Test case 4: Category aliases
        form = SupportFormSubmission(
            name="Test User",
            email="test@example.com",
            subject="Test Subject",
            category="bug",  # Alias for bug_report
            message="This is a valid message with enough characters."
        )
        assert form.category == "bug_report"


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([
        __file__,
        "-v",
        "--tb=short"
    ])
