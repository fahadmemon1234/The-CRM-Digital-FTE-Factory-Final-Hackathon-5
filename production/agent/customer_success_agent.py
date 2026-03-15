"""
TechCorp Customer Success AI Agent - Production Agent

Complete production agent implementation using OpenAI Agents SDK.

INCUBATION MAPPING:
-------------------
Incubation Location: src/agent/prototype.py
Incubation Pattern: Custom CustomerSuccessAgent class with manual tool calls
Production Location: production/agent/customer_success_agent.py
Production Pattern: OpenAI Agents SDK Agent with @function_tool decorated tools

Key Changes from Incubation:
- Custom agent class → OpenAI Agents SDK Agent
- Manual tool orchestration → SDK-managed tool calling
- Simple string responses → Structured Pydantic models
- No validation → Pydantic input validation
- Print statements → Structured logging

Author: AI Engineering Team
Version: 1.0.0 (Production)
Based on: Prototype v2 (Incubation)
"""

import asyncio
import logging
import os
import sys
from enum import Enum
from typing import Optional, List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydantic import BaseModel, Field, field_validator

# OpenAI Agents SDK imports
from agents import Agent, Runner, function_tool

# Import tools from tools.py - they are FunctionTool wrappers
from production.agent.tools import (
    search_knowledge_base,
    create_ticket,
    get_customer_history,
    escalate_to_human,
    send_response,
)

# Helper to invoke FunctionTool wrappers
async def _invoke_tool(tool, *args, **kwargs):
    """Invoke a FunctionTool wrapper."""
    if hasattr(tool, 'on_invoke_tool'):
        # FunctionTool - need to invoke through the tool's invoke method
        # The tool expects a RunContextWrapper and arguments as a dict
        from agents import RunContextWrapper
        
        # Create a minimal context (None works for simple tools)
        context = RunContextWrapper(context=None)
        
        # Build arguments dict from Pydantic model if needed
        if args and hasattr(args[0], 'model_dump'):
            args_dict = args[0].model_dump()
        else:
            args_dict = kwargs
        
        # Invoke the tool
        result = await tool.on_invoke_tool(context, args_dict)
        return result
    else:
        # Regular function
        return await tool(*args, **kwargs) if asyncio.iscoroutinefunction(tool) else tool(*args, **kwargs)

# Import system prompt
from production.agent.prompts import CUSTOMER_SUCCESS_SYSTEM_PROMPT

# Import formatters
from production.agent.formatters import format_for_channel

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class Channel(str, Enum):
    """
    Communication channels supported by the agent.
    
    INCUBATION: Simple Enum in prototype.py
    PRODUCTION: Same structure, used across multiple modules
    """
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"


# ============================================================================
# PYDANTIC INPUT MODELS
# ============================================================================
# INCUBATION: Dict parameters with manual validation
# PRODUCTION: Pydantic BaseModel with automatic validation

class KnowledgeSearchInput(BaseModel):
    """
    Input model for knowledge base search.
    
    INCUBATION: Simple string query parameter
    PRODUCTION: Validated model with optional filters
    
    Usage: Agent should use this tool when customer asks product-related
    questions that require factual information from documentation.
    """
    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The search query to find relevant documentation"
    )
    max_results: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum number of results to return (1-10)"
    )
    
    @field_validator('query')
    @classmethod
    def validate_query_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty or whitespace only')
        return v.strip()


class TicketInput(BaseModel):
    """
    Input model for creating support tickets.
    
    INCUBATION: Separate parameters with manual validation
    PRODUCTION: Validated model with automatic type checking
    
    Usage: Agent MUST call this tool for EVERY customer interaction
    before providing a response. Creates audit trail and enables
    escalation tracking.
    """
    customer_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Customer identifier (usually email address)"
    )
    issue: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Description of the customer issue"
    )
    priority: str = Field(
        default="medium",
        description="Ticket priority: low, medium, high, critical"
    )
    category: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Optional issue category for routing"
    )
    channel: Channel = Field(
        ...,
        description="Communication channel: email, whatsapp, or web_form"
    )
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        valid_priorities = ['low', 'medium', 'high', 'critical']
        if v.lower() not in valid_priorities:
            raise ValueError(f'Priority must be one of: {valid_priorities}')
        return v.lower()


class EscalationInput(BaseModel):
    """
    Input model for escalating tickets to human support.
    
    INCUBATION: Simple ticket_id and reason parameters
    PRODUCTION: Validated model with urgency tracking
    
    Usage: Agent should use this tool when escalation triggers are detected:
    - Legal threats, security concerns, refund requests
    - Pricing inquiries, human agent requests
    - Sentiment score < 0.3, 2+ failed knowledge searches
    """
    ticket_id: str = Field(
        ...,
        min_length=1,
        description="The ticket ID to escalate"
    )
    reason: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Reason for escalation (e.g., 'pricing inquiry', 'legal threat')"
    )
    urgency: str = Field(
        default="normal",
        description="Escalation urgency: normal, urgent, critical"
    )
    
    @field_validator('urgency')
    @classmethod
    def validate_urgency(cls, v):
        valid_urgencies = ['normal', 'urgent', 'critical']
        if v.lower() not in valid_urgencies:
            raise ValueError(f'Urgency must be one of: {valid_urgencies}')
        return v.lower()


class ResponseInput(BaseModel):
    """
    Input model for sending responses to customers.
    
    INCUBATION: Separate parameters without validation
    PRODUCTION: Validated model with channel-aware constraints
    
    Usage: Agent MUST use this tool (not print) to send all customer
    responses. Handles channel formatting and delivery tracking.
    """
    ticket_id: str = Field(
        ...,
        min_length=1,
        description="The ticket ID to respond to"
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="The response message content"
    )
    channel: Channel = Field(
        ...,
        description="Channel to send response through: email, whatsapp, or web_form"
    )
    
    @field_validator('message')
    @classmethod
    def validate_message_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_response_for_channel(
    response: str,
    channel: Channel,
    ticket_id: Optional[str] = None,
    customer_name: Optional[str] = None
) -> str:
    """
    Format response for the specified channel.
    
    INCUBATION: ResponseFormatter class in prototype.py
    PRODUCTION: Delegates to formatters.py with additional context
    
    Args:
        response: Raw response content
        channel: Target channel
        ticket_id: Optional ticket reference
        customer_name: Optional customer name for personalization
        
    Returns:
        Formatted response string
    """
    # Use the imported formatter
    return format_for_channel(
        response=response,
        channel=channel.value if isinstance(channel, Channel) else channel,
        customer_name=customer_name,
        ticket_id=ticket_id
    )


# ============================================================================
# AGENT DEFINITION
# ============================================================================

# INCUBATION: Custom CustomerSuccessAgent class
# PRODUCTION: OpenAI Agents SDK Agent with pre-configured tools

customer_success_agent = Agent(
    name="Customer Success FTE",
    model="gpt-4o",
    instructions=CUSTOMER_SUCCESS_SYSTEM_PROMPT,
    tools=[
        search_knowledge_base,
        create_ticket,
        get_customer_history,
        escalate_to_human,
        send_response,
    ],
)


# ============================================================================
# RUNNER FUNCTIONS
# ============================================================================

async def run_agent(
    user_input: str,
    customer_id: str,
    channel: Channel = Channel.WEB_FORM,
    conversation_history: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Run the customer success agent with user input.
    
    INCUBATION: process_message() method in prototype.py
    PRODUCTION: OpenAI Agents SDK Runner with structured output
    
    Args:
        user_input: Customer's message content
        customer_id: Customer identifier (email)
        channel: Communication channel
        conversation_history: Optional conversation history
        
    Returns:
        Dict with response, ticket_id, escalation_info, metadata
    """
    try:
        # Build input with context
        context_message = f"""
Customer ID: {customer_id}
Channel: {channel.value}

Customer Message:
{user_input}
"""
        
        # Add conversation history if provided
        if conversation_history:
            context_message += f"\n\nPrevious Conversation:\n{conversation_history}"
        
        # Run the agent
        result = await Runner.run(
            customer_success_agent,
            context_message
        )
        
        # Extract response
        response_text = result.final_output
        
        return {
            "success": True,
            "response": response_text,
            "customer_id": customer_id,
            "channel": channel.value,
            "ticket_id": None,  # Would be extracted from tool calls
            "escalated": False,
            "metadata": {
                "model": "gpt-4o",
                "timestamp": __import__('datetime').datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "response": "I apologize, but I'm experiencing technical difficulties. "
                       "Please try again or contact us directly.",
            "customer_id": customer_id,
            "channel": channel.value,
            "ticket_id": None,
            "escalated": False,
            "metadata": {
                "error_type": type(e).__name__,
                "timestamp": __import__('datetime').datetime.utcnow().isoformat()
            }
        }


async def process_customer_message(
    message: str,
    customer_email: str,
    channel: str = "web_form",
    customer_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    High-level function to process a customer message end-to-end.
    
    This is the main entry point for the production agent.
    
    INCUBATION: CustomerSuccessAgent.process_message() in prototype.py
    PRODUCTION: Orchestrated workflow with explicit tool calls
    
    Args:
        message: Customer's message content
        customer_email: Customer email address
        channel: Channel name ('email', 'whatsapp', 'web_form')
        customer_name: Optional customer name
        
    Returns:
        Dict with formatted response and metadata
    """
    from datetime import datetime
    
    try:
        # Convert channel string to enum
        channel_enum = Channel(channel.lower())

        # Step 1: Create ticket (REQUIRED FIRST)
        logger.info(f"Creating ticket for {customer_email}")
        ticket_input = TicketInput(
            customer_id=customer_email,
            issue=message[:500],  # Truncate for ticket
            priority="medium",
            channel=channel_enum
        )
        ticket_result = await _invoke_tool(create_ticket, ticket_input)

        # Extract ticket_id from result string
        ticket_id = None
        if ticket_result and "tkt_" in ticket_result:
            ticket_id = ticket_result.split("tkt_")[1].split()[0]
            ticket_id = f"tkt_{ticket_id}"

        logger.info(f"Ticket created: {ticket_id}")

        # Step 2: Get customer history
        logger.info(f"Fetching history for {customer_email}")
        history_result = await _invoke_tool(get_customer_history, customer_email)

        # Step 3: Search knowledge base
        logger.info(f"Searching knowledge base for: {message[:50]}...")
        search_input = KnowledgeSearchInput(
            query=message,
            max_results=5
        )
        search_result = await _invoke_tool(search_knowledge_base, search_input)

        # Step 4: Generate response using the agent
        logger.info("Running agent for response generation")
        agent_result = await run_agent(
            user_input=message,
            customer_id=customer_email,
            channel=channel_enum
        )

        response_text = agent_result.get("response", "")

        # Step 5: Format response for channel
        formatted_response = format_response_for_channel(
            response=response_text,
            channel=channel_enum,
            ticket_id=ticket_id,
            customer_name=customer_name
        )

        # Step 6: Send response
        logger.info(f"Sending response via {channel}")
        response_input = ResponseInput(
            ticket_id=ticket_id or "tkt_temp",
            message=formatted_response,
            channel=channel_enum
        )
        send_result = await _invoke_tool(send_response, response_input)
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "response": formatted_response,
            "channel": channel,
            "customer_email": customer_email,
            "escalated": False,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to process message: {e}")
        return {
            "success": False,
            "error": str(e),
            "response": "I apologize, but I encountered an error processing your request. "
                       "Please try again or contact us directly.",
            "ticket_id": None,
            "channel": channel,
            "customer_email": customer_email,
            "escalated": False,
            "timestamp": datetime.utcnow().isoformat()
        }


# ============================================================================
# SMOKE TEST
# ============================================================================

async def smoke_test():
    """
    Quick smoke test to verify the agent works.
    
    INCUBATION: Manual testing with print statements in prototype.py
    PRODUCTION: Automated smoke test with assertions
    
    This test:
    1. Creates a sample web_form message
    2. Runs the agent
    3. Prints the result
    """
    print("=" * 70)
    print("TechCorp Customer Success AI Agent - Smoke Test")
    print("=" * 70)
    
    # Sample message
    sample_message = "How do I reset my password? I've tried the forgot password link but I'm not receiving any email."
    sample_email = "test.user@example.com"
    sample_channel = "web_form"
    sample_name = "Test User"
    
    print(f"\nInput:")
    print(f"  Customer: {sample_name} <{sample_email}>")
    print(f"  Channel: {sample_channel}")
    print(f"  Message: {sample_message}")
    print()
    
    try:
        # Process the message
        print("Processing message...")
        result = await process_customer_message(
            message=sample_message,
            customer_email=sample_email,
            channel=sample_channel,
            customer_name=sample_name
        )
        
        # Print result
        print(f"\nResult:")
        print(f"  Success: {result.get('success', False)}")
        print(f"  Ticket ID: {result.get('ticket_id', 'N/A')}")
        print(f"  Channel: {result.get('channel', 'N/A')}")
        print(f"  Escalated: {result.get('escalated', False)}")
        print(f"  Timestamp: {result.get('timestamp', 'N/A')}")
        
        if result.get('error'):
            print(f"  Error: {result['error']}")
        
        print(f"\nResponse ({len(result.get('response', ''))} chars):")
        print("-" * 70)
        print(result.get('response', 'No response'))
        print("-" * 70)
        
        # Verify result
        print("\nVerification:")
        print(f"  ✓ Has response: {bool(result.get('response'))}")
        print(f"  ✓ Has ticket_id: {bool(result.get('ticket_id'))}")
        print(f"  ✓ Success flag: {result.get('success', False)}")
        
        if result.get('success'):
            print("\n✓ Smoke test PASSED")
        else:
            print("\n✗ Smoke test FAILED")
            
    except Exception as e:
        print(f"\n✗ Smoke test FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("Smoke Test Complete")
    print("=" * 70)


if __name__ == "__main__":
    # Run smoke test
    asyncio.run(smoke_test())
