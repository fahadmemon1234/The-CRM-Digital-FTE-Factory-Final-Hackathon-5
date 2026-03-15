"""
TechCorp Customer Success AI Agent - MCP Server

Exposes customer success capabilities as Model Context Protocol (MCP) tools.
"""

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server
from enum import Enum
from typing import Any
import uuid
import json
from datetime import datetime


class Channel(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"


# In-memory storage
tickets: dict[str, dict[str, Any]] = {}
customer_history: dict[str, list[dict[str, Any]]] = {}
escalations: dict[str, dict[str, Any]] = {}

# Initialize server
server = Server("customer-success-fte")


def load_product_docs() -> str:
    """Load product documentation from context file."""
    try:
        with open("context/product-docs.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def search_docs(query: str, top_k: int = 3) -> list[dict[str, Any]]:
    """Search product docs for relevant sections."""
    content = load_product_docs()
    if not content:
        return []
    
    # Parse into sections
    sections = {}
    current_section = "introduction"
    current_content = []
    
    for line in content.split("\n"):
        if line.startswith("## "):
            if current_content:
                sections[current_section] = "\n".join(current_content)
            current_section = line.replace("## ", "").strip().lower()
            current_content = []
        else:
            current_content.append(line)
    
    if current_content:
        sections[current_section] = "\n".join(current_content)
    
    # Score sections by query match
    query_terms = query.lower().split()
    results = []
    
    for section, content in sections.items():
        content_lower = content.lower()
        score = sum(1 for term in query_terms if term in content_lower)
        
        if score > 0:
            # Find relevant excerpt
            excerpt = find_excerpt(content, query_terms)
            results.append({
                "section": section,
                "excerpt": excerpt,
                "score": score
            })
    
    # Sort by score and return top_k
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


def find_excerpt(content: str, terms: list[str]) -> str:
    """Find a relevant excerpt containing search terms."""
    lines = content.split("\n")
    for line in lines:
        if any(term in line.lower() for term in terms):
            return line.strip()[:200]
    return content[:200].strip()


def format_for_channel(message: str, channel: Channel) -> str:
    """Format message for specific channel."""
    if channel == Channel.EMAIL:
        return f"""Dear Customer,

Thank you for reaching out to TechCorp Support.

{message}

If you have any other questions, please don't hesitate to reach out.

Best regards,
TechCorp AI Support Team
support@techcorp.com"""
    
    elif channel == Channel.WHATSAPP:
        # Trim to 300 characters
        if len(message) > 300:
            message = message[:297] + "..."
        return message
    
    elif channel == Channel.WEB_FORM:
        return f"""Hello,

Thanks for contacting TechCorp Support.

{message}

Feel free to reach out if you have any other questions.

Best,
TechCorp Support"""
    
    return message


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="search_knowledge_base",
            description="Search the TechCorp product documentation for relevant information. Returns top 3 relevant sections with excerpts.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find relevant documentation"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="create_ticket",
            description="Create a new support ticket for a customer issue. Returns a ticket ID for tracking.",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "Customer identifier (usually email address)"
                    },
                    "issue": {
                        "type": "string",
                        "description": "Description of the customer issue"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Priority level of the ticket"
                    },
                    "channel": {
                        "type": "string",
                        "enum": ["email", "whatsapp", "web_form"],
                        "description": "Channel through which the issue was reported"
                    }
                },
                "required": ["customer_id", "issue", "priority", "channel"]
            }
        ),
        Tool(
            name="get_customer_history",
            description="Retrieve all past interactions for a customer across all channels (email, whatsapp, web_form).",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "Customer identifier (usually email address)"
                    }
                },
                "required": ["customer_id"]
            }
        ),
        Tool(
            name="escalate_to_human",
            description="Escalate a ticket to human support team. Returns escalation confirmation with escalation ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string",
                        "description": "The ticket ID to escalate"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for escalation (e.g., 'pricing inquiry', 'legal threat', 'security concern')"
                    }
                },
                "required": ["ticket_id", "reason"]
            }
        ),
        Tool(
            name="send_response",
            description="Send a response to a ticket, formatted appropriately for the channel. Returns delivery status.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string",
                        "description": "The ticket ID to respond to"
                    },
                    "message": {
                        "type": "string",
                        "description": "The response message content"
                    },
                    "channel": {
                        "type": "string",
                        "enum": ["email", "whatsapp", "web_form"],
                        "description": "Channel to send the response through"
                    }
                },
                "required": ["ticket_id", "message", "channel"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    
    if name == "search_knowledge_base":
        query = arguments.get("query", "")
        results = search_docs(query)
        
        if not results:
            return [TextContent(
                type="text",
                text="No relevant documentation found for the query."
            )]
        
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(f"--- Result {i} ---")
            formatted.append(f"Section: {result['section']}")
            formatted.append(f"Relevance Score: {result['score']}")
            formatted.append(f"Excerpt: {result['excerpt']}")
            formatted.append("")
        
        return [TextContent(
            type="text",
            text="\n".join(formatted)
        )]
    
    elif name == "create_ticket":
        customer_id = arguments.get("customer_id", "")
        issue = arguments.get("issue", "")
        priority = arguments.get("priority", "medium")
        channel_str = arguments.get("channel", "email")
        
        # Convert string to Channel enum
        channel = Channel(channel_str)
        
        ticket_id = str(uuid.uuid4())
        ticket = {
            "ticket_id": ticket_id,
            "customer_id": customer_id,
            "issue": issue,
            "priority": priority,
            "channel": channel.value,
            "status": "open",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "messages": [],
            "escalated": False,
            "escalation_id": None
        }
        
        tickets[ticket_id] = ticket
        
        # Add to customer history
        if customer_id not in customer_history:
            customer_history[customer_id] = []
        customer_history[customer_id].append({
            "type": "ticket_created",
            "ticket_id": ticket_id,
            "timestamp": ticket["created_at"]
        })
        
        return [TextContent(
            type="text",
            text=f"Ticket created successfully!\n\nTicket ID: {ticket_id}\nCustomer: {customer_id}\nPriority: {priority}\nChannel: {channel.value}\nStatus: open\nCreated: {ticket['created_at']}"
        )]
    
    elif name == "get_customer_history":
        customer_id = arguments.get("customer_id", "")
        
        if customer_id not in customer_history:
            return [TextContent(
                type="text",
                text=f"No history found for customer: {customer_id}"
            )]
        
        history = customer_history[customer_id]
        
        # Get all tickets for this customer
        customer_tickets = [
            t for t in tickets.values() 
            if t["customer_id"] == customer_id
        ]
        
        formatted = []
        formatted.append(f"=== Customer History for {customer_id} ===\n")
        
        # Show tickets
        formatted.append(f"Total Tickets: {len(customer_tickets)}")
        formatted.append("")
        
        for ticket in customer_tickets:
            formatted.append(f"--- Ticket: {ticket['ticket_id']} ---")
            formatted.append(f"Status: {ticket['status']}")
            formatted.append(f"Priority: {ticket['priority']}")
            formatted.append(f"Channel: {ticket['channel']}")
            formatted.append(f"Escalated: {'Yes' if ticket['escalated'] else 'No'}")
            formatted.append(f"Created: {ticket['created_at']}")
            if ticket["messages"]:
                formatted.append(f"Messages: {len(ticket['messages'])}")
            formatted.append("")
        
        # Show interaction timeline
        formatted.append("--- Interaction Timeline ---")
        for event in sorted(history, key=lambda x: x.get("timestamp", "")):
            formatted.append(f"[{event.get('timestamp', 'N/A')}] {event.get('type', 'unknown')}")
        
        return [TextContent(
            type="text",
            text="\n".join(formatted)
        )]
    
    elif name == "escalate_to_human":
        ticket_id = arguments.get("ticket_id", "")
        reason = arguments.get("reason", "Unspecified")
        
        if ticket_id not in tickets:
            return [TextContent(
                type="text",
                text=f"Error: Ticket not found: {ticket_id}"
            )]
        
        escalation_id = str(uuid.uuid4())
        escalation = {
            "escalation_id": escalation_id,
            "ticket_id": ticket_id,
            "reason": reason,
            "escalated_at": datetime.utcnow().isoformat(),
            "status": "pending"
        }
        
        escalations[escalation_id] = escalation
        
        # Update ticket
        tickets[ticket_id]["escalated"] = True
        tickets[ticket_id]["escalation_id"] = escalation_id
        tickets[ticket_id]["status"] = "escalated"
        tickets[ticket_id]["updated_at"] = datetime.utcnow().isoformat()
        
        # Add to customer history
        customer_id = tickets[ticket_id]["customer_id"]
        if customer_id not in customer_history:
            customer_history[customer_id] = []
        customer_history[customer_id].append({
            "type": "escalation",
            "escalation_id": escalation_id,
            "ticket_id": ticket_id,
            "reason": reason,
            "timestamp": escalation["escalated_at"]
        })
        
        # Determine team based on reason
        reason_lower = reason.lower()
        if "pricing" in reason_lower or "discount" in reason_lower:
            team = "Sales Team"
        elif "refund" in reason_lower or "chargeback" in reason_lower:
            team = "Billing Team"
        elif "legal" in reason_lower or "lawyer" in reason_lower or "gdpr" in reason_lower:
            team = "Legal Team"
        elif "security" in reason_lower or "breach" in reason_lower:
            team = "Security Team"
        else:
            team = "Senior Support"
        
        return [TextContent(
            type="text",
            text=f"=== Escalation Confirmed ===\n\nEscalation ID: {escalation_id}\nTicket ID: {ticket_id}\nReason: {reason}\nAssigned Team: {team}\nStatus: pending\nEscalated At: {escalation['escalated_at']}\n\nThe {team} will respond within the SLA timeframe for this priority."
        )]
    
    elif name == "send_response":
        ticket_id = arguments.get("ticket_id", "")
        message = arguments.get("message", "")
        channel_str = arguments.get("channel", "email")
        
        if ticket_id not in tickets:
            return [TextContent(
                type="text",
                text=f"Error: Ticket not found: {ticket_id}"
            )]
        
        channel = Channel(channel_str)
        
        # Format message for channel
        formatted_message = format_for_channel(message, channel)
        
        # Simulate sending
        timestamp = datetime.utcnow().isoformat()
        
        # Add to ticket messages
        tickets[ticket_id]["messages"].append({
            "role": "agent",
            "content": formatted_message,
            "channel": channel.value,
            "timestamp": timestamp
        })
        tickets[ticket_id]["updated_at"] = timestamp
        
        # Add to customer history
        customer_id = tickets[ticket_id]["customer_id"]
        if customer_id not in customer_history:
            customer_history[customer_id] = []
        customer_history[customer_id].append({
            "type": "response_sent",
            "ticket_id": ticket_id,
            "channel": channel.value,
            "timestamp": timestamp
        })
        
        # Simulate delivery confirmation
        delivery_status = "delivered"
        
        return [TextContent(
            type="text",
            text=f"=== Response Sent ===\n\nTicket ID: {ticket_id}\nChannel: {channel.value}\nDelivery Status: {delivery_status}\nTimestamp: {timestamp}\nMessage Length: {len(formatted_message)} chars\n\n--- Formatted Message ---\n{formatted_message}"
        )]
    
    else:
        return [TextContent(
            type="text",
            text=f"Error: Unknown tool: {name}"
        )]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
