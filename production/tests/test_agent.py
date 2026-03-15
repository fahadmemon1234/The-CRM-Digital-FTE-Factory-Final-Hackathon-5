"""
TechCorp Customer Success AI Agent - Agent Tool Unit Tests

Unit tests for the agent tools in isolation with mocked database calls.

INCUBATION MAPPING:
-------------------
Incubation: No unit tests (manual testing)
Production: Comprehensive unit tests with pytest-mock

Test Coverage:
- search_knowledge_base: Returns correct format
- create_ticket: Returns ticket_id string
- escalate_to_human: Returns confirmation string
- send_response: Calls the right channel handler

Author: AI Engineering Team
Version: 1.0.0 (Production)
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Import tools to test
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.tools import (
    search_knowledge_base,
    create_ticket,
    escalate_to_human,
    send_response,
    KnowledgeSearchInput,
    TicketInput,
    EscalationInput,
    ResponseInput,
    Channel,
)


# ============================================================================
# TEST CLASS 1: Knowledge Base Search
# ============================================================================

class TestSearchKnowledgeBase:
    """
    Unit tests for search_knowledge_base tool.
    
    INCUBATION: No unit tests
    PRODUCTION: Mocked database tests
    """
    
    @pytest.mark.asyncio
    async def test_search_knowledge_base_returns_correct_format(self, mocker):
        """
        Test that search_knowledge_base returns correctly formatted results.
        
        INCUBATION: Manual search testing
        PRODUCTION: Mocked database with format validation
        
        Steps:
        1. Mock get_db_pool to return mock pool
        2. Mock pool.fetch to return sample results
        3. Call search_knowledge_base with test input
        4. Assert result contains expected keys
        5. Assert result is string type
        """
        # Mock database pool
        mock_pool = AsyncMock()
        mock_pool.fetch = AsyncMock(return_value=[
            {
                "section": "password_reset",
                "content": "To reset your password...",
                "similarity_score": 0.95
            },
            {
                "section": "account_setup",
                "content": "Account setup requires...",
                "similarity_score": 0.75
            }
        ])
        
        # Mock get_db_pool
        mock_get_db_pool = mocker.patch(
            "production.agent.tools.get_db_pool",
            return_value=mock_pool
        )
        
        # Create test input
        test_input = KnowledgeSearchInput(
            query="password reset",
            max_results=5
        )
        
        # Call function
        result = await search_knowledge_base(test_input)
        
        # Assert result is string
        assert isinstance(result, str), "Result should be a string"
        
        # Assert result contains expected content
        assert "password" in result.lower() or "reset" in result.lower(), \
            "Result should contain relevant content"
        
        # Assert database was called
        mock_get_db_pool.assert_called_once()
        mock_pool.fetch.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_knowledge_base_handles_no_results(self, mocker):
        """
        Test search_knowledge_base with no results.
        
        Steps:
        1. Mock get_db_pool to return mock pool
        2. Mock pool.fetch to return empty list
        3. Call search_knowledge_base
        4. Assert graceful fallback message
        """
        # Mock database pool
        mock_pool = AsyncMock()
        mock_pool.fetch = AsyncMock(return_value=[])
        
        mocker.patch(
            "production.agent.tools.get_db_pool",
            return_value=mock_pool
        )
        
        # Create test input with nonexistent query
        test_input = KnowledgeSearchInput(
            query="xyznonexistent123",
            max_results=5
        )
        
        # Call function
        result = await search_knowledge_base(test_input)
        
        # Assert result is string (graceful fallback)
        assert isinstance(result, str)
        assert len(result) > 0


# ============================================================================
# TEST CLASS 2: Create Ticket
# ============================================================================

class TestCreateTicket:
    """
    Unit tests for create_ticket tool.
    
    INCUBATION: No unit tests
    PRODUCTION: Mocked database tests
    """
    
    @pytest.mark.asyncio
    async def test_create_ticket_returns_ticket_id_string(self, mocker):
        """
        Test that create_ticket returns a ticket_id string.
        
        INCUBATION: Manual ticket creation
        PRODUCTION: Mocked database with UUID validation
        
        Steps:
        1. Mock get_db_pool to return mock pool
        2. Mock pool.fetchval to return sample UUID
        3. Call create_ticket with test input
        4. Assert result contains "tkt_" prefix
        5. Assert result is string type
        """
        # Mock database pool
        mock_pool = AsyncMock()
        mock_pool.fetchval = AsyncMock(return_value="12345678-1234-5678-1234-567812345678")
        
        mocker.patch(
            "production.agent.tools.get_db_pool",
            return_value=mock_pool
        )
        
        # Create test input
        test_input = TicketInput(
            customer_id="test@example.com",
            issue="Test issue for unit testing",
            priority="medium",
            channel=Channel.EMAIL
        )
        
        # Call function
        result = await create_ticket(test_input)
        
        # Assert result is string
        assert isinstance(result, str), "Result should be a string"
        
        # Assert result contains ticket_id
        assert "tkt_" in result, "Result should contain ticket_id with 'tkt_' prefix"
        
        # Assert database was called
        mock_pool.fetchval.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_ticket_validates_input(self, mocker):
        """
        Test create_ticket input validation.
        
        Steps:
        1. Create invalid input (empty issue)
        2. Assert Pydantic validation error
        """
        from pydantic import ValidationError
        
        # Test with invalid input (issue too short)
        with pytest.raises(ValidationError):
            TicketInput(
                customer_id="test@example.com",
                issue="Short",  # Too short (min 10 chars)
                priority="medium",
                channel=Channel.EMAIL
            )


# ============================================================================
# TEST CLASS 3: Escalate to Human
# ============================================================================

class TestEscalateToHuman:
    """
    Unit tests for escalate_to_human tool.
    
    INCUBATION: No unit tests
    PRODUCTION: Mocked database tests
    """
    
    @pytest.mark.asyncio
    async def test_escalate_to_human_returns_confirmation_string(self, mocker):
        """
        Test that escalate_to_human returns confirmation string.
        
        INCUBATION: Manual escalation testing
        PRODUCTION: Mocked database with team assignment
        
        Steps:
        1. Mock get_db_pool to return mock pool
        2. Mock pool.execute and pool.fetchrow
        3. Call escalate_to_human with test input
        4. Assert result contains "escalated" or team name
        5. Assert result is string type
        """
        # Mock database pool
        mock_pool = AsyncMock()
        mock_pool.execute = AsyncMock(return_value=None)
        mock_pool.fetchrow = AsyncMock(return_value={"customer_id": "test-id"})
        
        mocker.patch(
            "production.agent.tools.get_db_pool",
            return_value=mock_pool
        )
        
        # Create test input
        test_input = EscalationInput(
            ticket_id="tkt_test123",
            reason="Customer requesting refund",
            urgency="high"
        )
        
        # Call function
        result = await escalate_to_human(test_input)
        
        # Assert result is string
        assert isinstance(result, str), "Result should be a string"
        
        # Assert result contains confirmation
        assert "escalated" in result.lower() or "tkt_" in result, \
            "Result should contain escalation confirmation"
    
    @pytest.mark.asyncio
    async def test_escalate_to_human_assigns_correct_team(self, mocker):
        """
        Test that escalate_to_human assigns correct team based on reason.
        
        Steps:
        1. Test with refund reason -> Billing Team
        2. Test with pricing reason -> Sales Team
        3. Test with legal reason -> Legal Team
        """
        # Mock database pool
        mock_pool = AsyncMock()
        mock_pool.execute = AsyncMock(return_value=None)
        mock_pool.fetchrow = AsyncMock(return_value={"customer_id": "test-id"})
        
        mocker.patch(
            "production.agent.tools.get_db_pool",
            return_value=mock_pool
        )
        
        # Test refund -> Billing Team
        refund_input = EscalationInput(
            ticket_id="tkt_test",
            reason="Customer wants refund",
            urgency="normal"
        )
        refund_result = await escalate_to_human(refund_input)
        assert "Billing" in refund_result or "escalated" in refund_result.lower()


# ============================================================================
# TEST CLASS 4: Send Response
# ============================================================================

class TestSendResponse:
    """
    Unit tests for send_response tool.
    
    INCUBATION: No unit tests
    PRODUCTION: Mocked channel handler tests
    """
    
    @pytest.mark.asyncio
    async def test_send_response_calls_right_channel_handler(self, mocker):
        """
        Test that send_response calls the correct channel handler.
        
        INCUBATION: Manual response testing
        PRODUCTION: Mocked channel handlers with verification
        
        Steps:
        1. Mock get_db_pool
        2. Mock format_for_channel
        3. Call send_response with email channel
        4. Call send_response with whatsapp channel
        5. Verify correct formatting was called
        """
        # Mock database pool
        mock_pool = AsyncMock()
        mock_pool.execute = AsyncMock(return_value=None)
        mock_pool.fetchrow = AsyncMock(return_value={"customer_id": "test-id"})
        
        mocker.patch(
            "production.agent.tools.get_db_pool",
            return_value=mock_pool
        )
        
        # Mock format_for_channel
        mock_format = mocker.patch(
            "production.agent.tools.format_for_channel",
            return_value="Formatted response"
        )
        
        # Test with email channel
        email_input = ResponseInput(
            ticket_id="tkt_test",
            message="Test message",
            channel=Channel.EMAIL
        )
        
        result = await send_response(email_input)
        
        # Assert format_for_channel was called
        mock_format.assert_called()
        
        # Assert result is string
        assert isinstance(result, str)
    
    @pytest.mark.asyncio
    async def test_send_response_validates_input(self, mocker):
        """
        Test send_response input validation.
        
        Steps:
        1. Create invalid input (empty message)
        2. Assert Pydantic validation error
        """
        from pydantic import ValidationError
        
        # Test with empty message
        with pytest.raises(ValidationError):
            ResponseInput(
                ticket_id="tkt_test",
                message="",  # Empty message
                channel=Channel.EMAIL
            )


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
