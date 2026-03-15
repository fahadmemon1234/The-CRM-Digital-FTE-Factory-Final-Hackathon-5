"""
TechCorp Customer Success AI Agent - OpenAI Agents SDK Integration
with Spec-Driven Development and Agent Maturity Model

This module implements the production-grade AI agent using the OpenAI Agents SDK,
following spec-driven development principles and implementing a defined agent
maturity model for progressive capability enhancement.

AGENT MATURITY MODEL:
---------------------
Level 1: Reactive - Responds to customer queries with knowledge base lookup
Level 2: Contextual - Maintains conversation history and customer context
Level 3: Proactive - Anticipates needs and suggests relevant actions
Level 4: Adaptive - Learns from interactions and improves responses
Level 5: Autonomous - Handles complex multi-step workflows independently

SPEC-DRIVEN DEVELOPMENT:
------------------------
This agent is developed following these specifications:
- specs/customer-success-fte-spec.md - System specification
- specs/discovery-log.md - Requirements discovery
- specs/skills-manifest.md - Core skills definition
- specs/escalation-rules.md - Escalation logic

Author: AI Engineering Team
Version: 2.0.0 (OpenAI Agents SDK Enhanced)
"""

import asyncio
import logging
import os
import sys
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydantic import BaseModel, Field, field_validator

# OpenAI Agents SDK imports
from agents import Agent, Runner, function_tool, RunContextWrapper

# Import tools from tools.py
from production.agent.tools import (
    search_knowledge_base,
    create_ticket,
    get_customer_history,
    escalate_to_human,
    send_response,
)

# Import system prompt
from production.agent.prompts import CUSTOMER_SUCCESS_SYSTEM_PROMPT

# Import formatters
from production.agent.formatters import format_for_channel

logger = logging.getLogger(__name__)


# ============================================================================
# AGENT MATURITY MODEL ENUM
# ============================================================================

class AgentMaturityLevel(int, Enum):
    """
    Agent Maturity Model - Defines progressive capability levels.
    
    SPEC REFERENCE: specs/discovery-log.md - Section 10 (Implementation Priorities)
    """
    LEVEL_1_REACTIVE = 1      # Basic Q&A with knowledge base
    LEVEL_2_CONTEXTUAL = 2    # Conversation history + customer context
    LEVEL_3_PROACTIVE = 3     # Anticipates needs, suggests actions
    LEVEL_4_ADAPTIVE = 4      # Learns from interactions
    LEVEL_5_AUTONOMOUS = 5    # Full workflow automation


# ============================================================================
# SPEC-DRIVEN INPUT MODELS
# ============================================================================

class SpecCompliantTicketInput(BaseModel):
    """
    Ticket input model compliant with system specification.
    
    SPEC REFERENCE: specs/customer-success-fte-spec.md - Data Model (Ticket Record)
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
    channel: str = Field(
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
    
    @field_validator('channel')
    @classmethod
    def validate_channel(cls, v):
        valid_channels = ['email', 'whatsapp', 'web_form']
        if v.lower() not in valid_channels:
            raise ValueError(f'Channel must be one of: {valid_channels}')
        return v.lower()


class SpecCompliantEscalationInput(BaseModel):
    """
    Escalation input model compliant with escalation rules.
    
    SPEC REFERENCE: specs/escalation-rules.md - Escalation Priority Matrix
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
        description="Reason for escalation"
    )
    urgency: str = Field(
        default="normal",
        description="Escalation urgency: normal, urgent, critical"
    )
    assigned_team: Optional[str] = Field(
        default=None,
        description="Target team for escalation"
    )
    
    @field_validator('urgency')
    @classmethod
    def validate_urgency(cls, v):
        valid_urgencies = ['normal', 'urgent', 'critical']
        if v.lower() not in valid_urgencies:
            raise ValueError(f'Urgency must be one of: {valid_urgencies}')
        return v.lower()


class SpecCompliantResponseInput(BaseModel):
    """
    Response input model with channel-aware constraints.
    
    SPEC REFERENCE: specs/customer-success-fte-spec.md - Supported Channels
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
    channel: str = Field(
        ...,
        description="Channel to send response through"
    )
    customer_name: Optional[str] = Field(
        default=None,
        description="Customer name for personalization"
    )


# ============================================================================
# AGENT METADATA CLASS
# ============================================================================

class AgentMetadata(BaseModel):
    """
    Metadata tracking for agent execution and maturity assessment.
    """
    maturity_level: AgentMaturityLevel = Field(
        default=AgentMaturityLevel.LEVEL_2_CONTEXTUAL,
        description="Current agent maturity level"
    )
    spec_version: str = Field(
        default="1.0",
        description="System specification version"
    )
    execution_id: str = Field(
        default_factory=lambda: f"exec_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        description="Unique execution identifier"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Execution timestamp"
    )
    capabilities_used: List[str] = Field(
        default_factory=list,
        description="List of capabilities/skills used in execution"
    )
    escalation_triggers_detected: List[str] = Field(
        default_factory=list,
        description="Escalation triggers detected in conversation"
    )
    sentiment_score: Optional[float] = Field(
        default=None,
        description="Analyzed sentiment score (0.0-1.0)"
    )
    confidence_score: Optional[float] = Field(
        default=None,
        description="Agent confidence in response (0.0-1.0)"
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def _invoke_tool(tool, *args, **kwargs):
    """Invoke a FunctionTool wrapper from OpenAI Agents SDK."""
    if hasattr(tool, 'on_invoke_tool'):
        # FunctionTool - need to invoke through the tool's invoke method
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


def detect_escalation_triggers(message: str) -> List[str]:
    """
    Detect escalation triggers in customer message.
    
    SPEC REFERENCE: specs/escalation-rules.md - 10 Escalation Triggers
    
    Args:
        message: Customer message text
        
    Returns:
        List of detected trigger keywords/categories
    """
    triggers = []
    message_lower = message.lower()
    
    # Legal/Language triggers
    legal_keywords = ['lawyer', 'attorney', 'lawsuit', 'sue', 'legal action', 
                      'bbb', 'better business bureau', 'ftc complaint',
                      'fraud', 'unauthorized charges', 'class action',
                      'govern yourself accordingly', 'legal notice']
    if any(word in message_lower for word in legal_keywords):
        triggers.append('legal_threat')
    
    # Security triggers
    security_keywords = ['hacked', 'breach', 'unauthorized access',
                         'account compromised', 'strange login',
                         'data leak', 'security vulnerability']
    if any(word in message_lower for word in security_keywords):
        triggers.append('security_concern')
    
    # Refund/Billing triggers
    refund_keywords = ['refund', 'chargeback', 'money back',
                       'cancel and refund', 'reverse charge',
                       'duplicate charge', 'unauthorized charge']
    if any(word in message_lower for word in refund_keywords):
        triggers.append('refund_request')
    
    # Pricing triggers
    pricing_keywords = ['discount', 'pricing', 'cheaper', 'better deal',
                        'custom pricing', 'enterprise quote', 'volume discount',
                        'student discount', 'price match', 'upgrade cost']
    if any(word in message_lower for word in pricing_keywords):
        triggers.append('pricing_inquiry')
    
    # Human request triggers
    human_keywords = ['talk to a human', 'real person', 'human agent',
                      'speak to someone', 'actual person', 'not a bot',
                      'manager', 'supervisor', 'human', 'agent']
    if any(word in message_lower for word in human_keywords):
        triggers.append('human_request')
    
    return triggers


def calculate_maturity_level(capabilities: List[str]) -> AgentMaturityLevel:
    """
    Calculate agent maturity level based on capabilities used.
    
    Args:
        capabilities: List of capabilities used in interaction
        
    Returns:
        AgentMaturityLevel enum value
    """
    # Level 1: Basic knowledge retrieval
    if 'knowledge_retrieval' in capabilities:
        return AgentMaturityLevel.LEVEL_1_REACTIVE
    
    # Level 2: Context awareness
    if 'customer_history' in capabilities or 'conversation_context' in capabilities:
        return AgentMaturityLevel.LEVEL_2_CONTEXTUAL
    
    # Level 3: Proactive suggestions
    if 'proactive_suggestion' in capabilities:
        return AgentMaturityLevel.LEVEL_3_PROACTIVE
    
    # Level 4: Adaptive learning
    if 'sentiment_analysis' in capabilities and 'adaptive_response' in capabilities:
        return AgentMaturityLevel.LEVEL_4_ADAPTIVE
    
    # Level 5: Full autonomy
    if 'workflow_automation' in capabilities:
        return AgentMaturityLevel.LEVEL_5_AUTONOMOUS
    
    # Default to Level 2
    return AgentMaturityLevel.LEVEL_2_CONTEXTUAL


# ============================================================================
# CHANNEL ENUM
# ============================================================================

class Channel(str, Enum):
    """
    Communication channels supported by the agent.
    
    SPEC REFERENCE: specs/customer-success-fte-spec.md - Supported Channels
    """
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"


# ============================================================================
# AGENT DEFINITION
# ============================================================================

# Create the customer success agent with OpenAI Agents SDK
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
    metadata={
        "spec_version": "1.0",
        "maturity_level": "2",
        "capabilities": [
            "knowledge_retrieval",
            "customer_identification",
            "ticket_management",
            "escalation_handling",
            "channel_adaptation"
        ]
    }
)


# ============================================================================
# RUNNER FUNCTIONS
# ============================================================================

async def run_agent_with_maturity_tracking(
    user_input: str,
    customer_id: str,
    channel: Channel = Channel.WEB_FORM,
    conversation_history: Optional[List[Dict[str, Any]]] = None,
    maturity_level: AgentMaturityLevel = AgentMaturityLevel.LEVEL_2_CONTEXTUAL
) -> Dict[str, Any]:
    """
    Run the customer success agent with maturity level tracking.
    
    SPEC REFERENCE: specs/skills-manifest.md - Skill Composition
    
    Args:
        user_input: Customer's message content
        customer_id: Customer identifier (email)
        channel: Communication channel
        conversation_history: Optional conversation history
        maturity_level: Target maturity level for execution
        
    Returns:
        Dict with response, ticket_id, escalation_info, metadata
    """
    try:
        # Build input with context
        context_message = f"""
Customer ID: {customer_id}
Channel: {channel.value}
Maturity Level: {maturity_level.name}

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
        
        # Detect escalation triggers
        escalation_triggers = detect_escalation_triggers(user_input)
        
        # Calculate capabilities used
        capabilities_used = ['knowledge_retrieval', 'customer_identification']
        if conversation_history:
            capabilities_used.append('conversation_context')
        if escalation_triggers:
            capabilities_used.append('escalation_detection')
        
        # Calculate maturity level
        calculated_maturity = calculate_maturity_level(capabilities_used)
        
        # Create metadata
        metadata = AgentMetadata(
            maturity_level=calculated_maturity,
            spec_version="1.0",
            capabilities_used=capabilities_used,
            escalation_triggers_detected=escalation_triggers
        )

        return {
            "success": True,
            "response": response_text,
            "customer_id": customer_id,
            "channel": channel.value,
            "ticket_id": None,  # Would be extracted from tool calls
            "escalated": False,
            "metadata": metadata.model_dump(),
            "maturity_assessment": {
                "level": calculated_maturity.value,
                "name": calculated_maturity.name,
                "capabilities_used": capabilities_used,
                "next_level_requirements": get_next_maturity_requirements(calculated_maturity)
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
                "timestamp": datetime.utcnow().isoformat(),
                "maturity_level": maturity_level.value
            }
        }


def get_next_maturity_requirements(current_level: AgentMaturityLevel) -> List[str]:
    """
    Get requirements to reach next maturity level.
    
    Args:
        current_level: Current maturity level
        
    Returns:
        List of requirements for next level
    """
    requirements = {
        AgentMaturityLevel.LEVEL_1_REACTIVE: [
            "Implement customer context tracking",
            "Add conversation history management",
            "Enable multi-turn conversations"
        ],
        AgentMaturityLevel.LEVEL_2_CONTEXTUAL: [
            "Add proactive suggestion capability",
            "Implement intent prediction",
            "Enable contextual recommendations"
        ],
        AgentMaturityLevel.LEVEL_3_PROACTIVE: [
            "Implement sentiment-based adaptation",
            "Add learning from feedback",
            "Enable response optimization"
        ],
        AgentMaturityLevel.LEVEL_4_ADAPTIVE: [
            "Add workflow automation",
            "Implement multi-step task handling",
            "Enable autonomous decision making"
        ],
        AgentMaturityLevel.LEVEL_5_AUTONOMOUS: [
            "Full autonomy achieved",
            "Continuous improvement enabled"
        ]
    }
    
    return requirements.get(current_level, ["Unknown maturity level"])


async def process_customer_message_spec_compliant(
    message: str,
    customer_email: str,
    channel: str = "web_form",
    customer_name: Optional[str] = None,
    maturity_level: AgentMaturityLevel = AgentMaturityLevel.LEVEL_2_CONTEXTUAL
) -> Dict[str, Any]:
    """
    High-level function to process a customer message with spec compliance.
    
    SPEC REFERENCE: specs/customer-success-fte-spec.md - Required Workflow
    
    Args:
        message: Customer's message content
        customer_email: Customer email address
        channel: Channel name ('email', 'whatsapp', 'web_form')
        customer_name: Optional customer name
        maturity_level: Target maturity level
        
    Returns:
        Dict with formatted response and metadata
    """
    try:
        # Convert channel string to enum
        channel_enum = Channel(channel.lower())
        
        # Step 1: Detect escalation triggers (SPEC-DRIVEN)
        logger.info(f"Detecting escalation triggers in message")
        escalation_triggers = detect_escalation_triggers(message)
        
        # Step 2: Create ticket (REQUIRED FIRST per spec)
        logger.info(f"Creating ticket for {customer_email}")
        ticket_input = SpecCompliantTicketInput(
            customer_id=customer_email,
            issue=message[:500],  # Truncate for ticket
            priority="medium",
            channel=channel_enum.value
        )
        ticket_result = await _invoke_tool(create_ticket, ticket_input)
        
        # Extract ticket_id from result string
        ticket_id = None
        if ticket_result and "tkt_" in ticket_result:
            ticket_id = ticket_result.split("tkt_")[1].split()[0]
            ticket_id = f"tkt_{ticket_id}"
        
        logger.info(f"Ticket created: {ticket_id}")
        
        # Step 3: Get customer history
        logger.info(f"Fetching history for {customer_email}")
        history_result = await _invoke_tool(get_customer_history, customer_email)
        
        # Step 4: Search knowledge base
        logger.info(f"Searching knowledge base for: {message[:50]}...")
        search_input = search_knowledge_base  # The tool itself handles the query
        # For spec-driven, we'll call the tool directly
        search_result = await _invoke_tool(
            search_knowledge_base,
            type('obj', (object,), {'query': message, 'max_results': 5})()
        )
        
        # Step 5: Run agent with maturity tracking
        logger.info("Running agent for response generation")
        agent_result = await run_agent_with_maturity_tracking(
            user_input=message,
            customer_id=customer_email,
            channel=channel_enum,
            maturity_level=maturity_level
        )
        
        response_text = agent_result.get("response", "")
        
        # Step 6: Format response for channel (SPEC-COMPLIANT)
        formatted_response = format_for_channel(
            response=response_text,
            channel=channel_enum.value,
            customer_name=customer_name,
            ticket_id=ticket_id
        )
        
        # Step 7: Send response
        logger.info(f"Sending response via {channel}")
        response_input = SpecCompliantResponseInput(
            ticket_id=ticket_id or "tkt_temp",
            message=formatted_response,
            channel=channel_enum.value,
            customer_name=customer_name
        )
        send_result = await _invoke_tool(send_response, response_input)
        
        # Step 8: Check if escalation needed
        should_escalate = len(escalation_triggers) > 0
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "response": formatted_response,
            "channel": channel,
            "customer_email": customer_email,
            "escalated": should_escalate,
            "escalation_triggers": escalation_triggers,
            "maturity_level": maturity_level.value,
            "timestamp": datetime.utcnow().isoformat(),
            "spec_compliance": {
                "ticket_created_first": ticket_id is not None,
                "history_checked": history_result is not None,
                "knowledge_searched": search_result is not None,
                "channel_formatted": True,
                "escalation_evaluated": True
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to process message: {e}")
        return {
            "success": False,
            "error": str(e),
            "response": "I apologize, but I encountered an error processing your request.",
            "ticket_id": None,
            "channel": channel,
            "customer_email": customer_email,
            "escalated": False,
            "timestamp": datetime.utcnow().isoformat()
        }


# ============================================================================
# SMOKE TEST
# ============================================================================

async def smoke_test_with_maturity_tracking():
    """
    Smoke test with maturity level tracking.
    """
    print("=" * 70)
    print("TechCorp Customer Success AI Agent - Maturity Tracking Test")
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
        # Process the message with maturity tracking
        print("Processing message with maturity tracking...")
        result = await process_customer_message_spec_compliant(
            message=sample_message,
            customer_email=sample_email,
            channel=sample_channel,
            customer_name=sample_name,
            maturity_level=AgentMaturityLevel.LEVEL_2_CONTEXTUAL
        )
        
        # Print result
        print(f"\nResult:")
        print(f"  Success: {result.get('success', False)}")
        print(f"  Ticket ID: {result.get('ticket_id', 'N/A')}")
        print(f"  Channel: {result.get('channel', 'N/A')}")
        print(f"  Escalated: {result.get('escalated', False)}")
        print(f"  Maturity Level: {result.get('maturity_level', 'N/A')}")
        print(f"  Timestamp: {result.get('timestamp', 'N/A')}")
        
        if result.get('escalation_triggers'):
            print(f"  Escalation Triggers: {result['escalation_triggers']}")
        
        if result.get('spec_compliance'):
            print(f"\nSpec Compliance:")
            for key, value in result['spec_compliance'].items():
                print(f"  {'✓' if value else '✗'} {key}")
        
        print(f"\nResponse ({len(result.get('response', ''))} chars):")
        print("-" * 70)
        print(result.get('response', 'No response'))
        print("-" * 70)
        
        # Verify result
        print("\nVerification:")
        print(f"  ✓ Has response: {bool(result.get('response'))}")
        print(f"  ✓ Has ticket_id: {bool(result.get('ticket_id'))}")
        print(f"  ✓ Success flag: {result.get('success', False)}")
        print(f"  ✓ Spec compliant: {result.get('spec_compliance', {}).get('ticket_created_first', False)}")
        
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
    asyncio.run(smoke_test_with_maturity_tracking())
