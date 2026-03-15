"""
TechCorp Customer Success AI Agent - Final Demo
Shows 5 diverse test cases with proper output formatting.
"""

import json
from prototype import CustomerSuccessAgent, CustomerMessage, Channel, load_sample_tickets


def demo():
    """Demonstrate the prototype with 5 carefully selected tickets."""
    print("=" * 70)
    print("TechCorp Customer Success AI Agent - Final Demo")
    print("Iterations Applied:")
    print("  1. Pricing queries always escalate")
    print("  2. Channel-aware response style")
    print("  3. Email: Dear [Name] + signature")
    print("  4. WhatsApp: Under 300 characters")
    print("=" * 70)
    
    agent = CustomerSuccessAgent()
    tickets = load_sample_tickets()
    
    # 5 diverse test cases
    test_cases = [
        (0, "Email - Invoice/Billing Question"),
        (1, "WhatsApp - Technical Support"),
        (5, "Web Form - Feature Request"),
        (40, "WhatsApp - Pricing/Discount Inquiry"),
        (54, "Email - Legal Threat (Critical)"),
    ]
    
    for idx, description in test_cases:
        ticket = tickets[idx]
        
        print(f"\n{'='*70}")
        print(f"TEST: {description}")
        print(f"Channel: {ticket['channel'].upper()} | Sentiment: {ticket['sentiment']}")
        print(f"{'='*70}")
        
        # Show customer message
        print(f"\n📩 CUSTOMER MESSAGE:")
        if ticket.get('subject'):
            print(f"   Subject: {ticket['subject']}")
        msg_preview = ticket['message'][:120].replace('\n', ' ')
        print(f"   \"{msg_preview}...\"")
        
        # Create and process message
        message = CustomerMessage(
            channel=Channel(ticket['channel']),
            message=ticket['message'],
            subject=ticket.get('subject'),
        )
        response = agent.process_message(message)
        
        # Show agent response
        print(f"\n🤖 AGENT RESPONSE:")
        print(f"   (Length: {len(response.response)} chars)")
        print()
        for line in response.response.split('\n'):
            print(f"   {line}")
        
        # Show analysis
        print(f"\n📊 ANALYSIS:")
        if response.escalation_needed:
            print(f"   ⚠️  ESCALATED to {response.escalation_team}")
            print(f"   Reason: {response.escalation_reason}")
        else:
            print(f"   ✓ Resolved by AI Agent")
        
        # Channel-specific verification
        print(f"\n📋 CHANNEL FORMAT CHECK:")
        if ticket['channel'] == 'email':
            has_dear = response.response.startswith("Dear")
            has_signature = "Best regards," in response.response
            print(f"   {'✓' if has_dear else '✗'} Has 'Dear' greeting")
            print(f"   {'✓' if has_signature else '✗'} Has signature block")
        elif ticket['channel'] == 'whatsapp':
            under_300 = len(response.response) <= 300
            print(f"   {'✓' if under_300 else '✗'} Under 300 characters ({len(response.response)} chars)")
        elif ticket['channel'] == 'web_form':
            has_hello = response.response.startswith("Hello")
            print(f"   {'✓' if has_hello else '✗'} Has 'Hello' greeting")
    
    print(f"\n{'='*70}")
    print("DEMO COMPLETE")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✓ Multi-channel support (Email, WhatsApp, Web Form)")
    print("  ✓ Channel-specific formatting")
    print("  ✓ Escalation detection (pricing, legal, refunds)")
    print("  ✓ Name extraction from messages")
    print("  ✓ Knowledge base search")
    print("=" * 70)


if __name__ == "__main__":
    demo()
