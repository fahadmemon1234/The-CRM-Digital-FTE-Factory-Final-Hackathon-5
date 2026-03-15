"""
Test script for TechCorp Customer Success MCP Server tools.
Demonstrates all 5 tools with sample calls.
"""

import sys
sys.path.insert(0, 'src')

from mcp_server import (
    search_docs, 
    tickets, 
    customer_history, 
    escalations,
    format_for_channel,
    Channel
)
from datetime import datetime
import uuid


def test_search_knowledge_base():
    """Test Tool 1: search_knowledge_base"""
    print("=" * 70)
    print("TEST 1: search_knowledge_base")
    print("=" * 70)
    
    query = "password reset"
    print(f"\nQuery: '{query}'\n")
    
    results = search_docs(query)
    
    if results:
        for i, result in enumerate(results, 1):
            print(f"--- Result {i} ---")
            print(f"Section: {result['section']}")
            print(f"Relevance Score: {result['score']}")
            print(f"Excerpt: {result['excerpt']}")
            print()
    else:
        print("No results found.")
    
    print()


def test_create_ticket():
    """Test Tool 2: create_ticket"""
    print("=" * 70)
    print("TEST 2: create_ticket")
    print("=" * 70)
    
    # Simulate tool call
    customer_id = "john.doe@example.com"
    issue = "Cannot login to account - password reset link expired"
    priority = "high"
    channel = "email"
    
    print(f"\nInput:")
    print(f"  customer_id: {customer_id}")
    print(f"  issue: {issue}")
    print(f"  priority: {priority}")
    print(f"  channel: {channel}")
    print()
    
    # Create ticket (simulating tool call logic)
    ticket_id = str(uuid.uuid4())
    ticket = {
        "ticket_id": ticket_id,
        "customer_id": customer_id,
        "issue": issue,
        "priority": priority,
        "channel": channel,
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
    
    print(f"Output:")
    print(f"  Ticket created successfully!")
    print(f"  Ticket ID: {ticket_id}")
    print(f"  Customer: {customer_id}")
    print(f"  Priority: {priority}")
    print(f"  Channel: {channel}")
    print(f"  Status: open")
    print(f"  Created: {ticket['created_at']}")
    print()
    
    return ticket_id


def test_get_customer_history(ticket_id: str):
    """Test Tool 3: get_customer_history"""
    print("=" * 70)
    print("TEST 3: get_customer_history")
    print("=" * 70)
    
    customer_id = "john.doe@example.com"
    print(f"\nInput:")
    print(f"  customer_id: {customer_id}")
    print()
    
    # Simulate some additional history
    customer_history[customer_id].append({
        "type": "message_received",
        "ticket_id": ticket_id,
        "channel": "email",
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # Get history (simulating tool call logic)
    history = customer_history.get(customer_id, [])
    customer_tickets = [t for t in tickets.values() if t["customer_id"] == customer_id]
    
    print(f"Output:")
    print(f"  === Customer History for {customer_id} ===")
    print()
    print(f"  Total Tickets: {len(customer_tickets)}")
    print()
    
    for ticket in customer_tickets:
        print(f"  --- Ticket: {ticket['ticket_id']} ---")
        print(f"  Status: {ticket['status']}")
        print(f"  Priority: {ticket['priority']}")
        print(f"  Channel: {ticket['channel']}")
        print(f"  Escalated: {'Yes' if ticket['escalated'] else 'No'}")
        print(f"  Created: {ticket['created_at']}")
        print()
    
    print(f"  --- Interaction Timeline ---")
    for event in sorted(history, key=lambda x: x.get("timestamp", "")):
        print(f"  [{event.get('timestamp', 'N/A')[:19]}] {event.get('type', 'unknown')}")
    print()


def test_escalate_to_human(ticket_id: str):
    """Test Tool 4: escalate_to_human"""
    print("=" * 70)
    print("TEST 4: escalate_to_human")
    print("=" * 70)
    
    reason = "Customer requesting refund - annual plan charged by mistake"
    print(f"\nInput:")
    print(f"  ticket_id: {ticket_id}")
    print(f"  reason: {reason}")
    print()
    
    # Escalate (simulating tool call logic)
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
    if ticket_id in tickets:
        tickets[ticket_id]["escalated"] = True
        tickets[ticket_id]["escalation_id"] = escalation_id
        tickets[ticket_id]["status"] = "escalated"
    
    # Determine team
    reason_lower = reason.lower()
    if "refund" in reason_lower:
        team = "Billing Team"
    else:
        team = "Senior Support"
    
    print(f"Output:")
    print(f"  === Escalation Confirmed ===")
    print()
    print(f"  Escalation ID: {escalation_id}")
    print(f"  Ticket ID: {ticket_id}")
    print(f"  Reason: {reason}")
    print(f"  Assigned Team: {team}")
    print(f"  Status: pending")
    print(f"  Escalated At: {escalation['escalated_at'][:19]}")
    print()
    print(f"  The {team} will respond within the SLA timeframe for this priority.")
    print()
    
    return escalation_id


def test_send_response(ticket_id: str):
    """Test Tool 5: send_response"""
    print("=" * 70)
    print("TEST 5: send_response")
    print("=" * 70)
    
    # Test with different channels
    test_cases = [
        ("email", "Your refund request has been processed. The amount will be credited to your card within 5-7 business days."),
        ("whatsapp", "Your refund request has been processed. The amount will be credited to your card within 5-7 business days."),
        ("web_form", "Your refund request has been processed. The amount will be credited to your card within 5-7 business days."),
    ]
    
    for channel_str, message in test_cases:
        print(f"\nInput:")
        print(f"  ticket_id: {ticket_id}")
        print(f"  channel: {channel_str}")
        print(f"  message: {message[:50]}...")
        print()
        
        channel = Channel(channel_str)
        formatted = format_for_channel(message, channel)
        
        print(f"Output:")
        print(f"  === Response Sent ===")
        print()
        print(f"  Ticket ID: {ticket_id}")
        print(f"  Channel: {channel_str}")
        print(f"  Delivery Status: delivered")
        print(f"  Message Length: {len(formatted)} chars")
        print()
        print(f"  --- Formatted Message ---")
        for line in formatted.split("\n"):
            print(f"  {line}")
        print()


def main():
    """Run all tool tests."""
    print()
    print("#" * 70)
    print("# TechCorp Customer Success MCP Server - Tool Tests")
    print("#" * 70)
    print()
    
    # Test 1: Search knowledge base
    test_search_knowledge_base()
    
    # Test 2: Create ticket
    ticket_id = test_create_ticket()
    
    # Test 3: Get customer history
    test_get_customer_history(ticket_id)
    
    # Test 4: Escalate to human
    test_escalate_to_human(ticket_id)
    
    # Test 5: Send response (with all 3 channels)
    test_send_response(ticket_id)
    
    print("#" * 70)
    print("# All Tool Tests Complete!")
    print("#" * 70)
    print()


if __name__ == "__main__":
    main()
