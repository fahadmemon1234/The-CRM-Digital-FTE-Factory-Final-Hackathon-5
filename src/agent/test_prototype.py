"""
TechCorp Customer Success AI Agent - Extended Test Suite
Tests the prototype with diverse sample tickets.
"""

import json
from typing import List, Dict
from prototype import (
    CustomerSuccessAgent, CustomerMessage, Channel, load_sample_tickets
)


def run_extended_tests():
    """Run extended tests with diverse ticket scenarios."""
    print("=" * 70)
    print("TechCorp Customer Success AI Agent - Extended Test Suite")
    print("=" * 70)
    
    agent = CustomerSuccessAgent()
    tickets = load_sample_tickets()
    
    if not tickets:
        print("\nError: Could not load sample tickets.")
        return
    
    # Select diverse tickets covering all channels and categories
    test_cases = [
        # (index, description)
        (0, "Email - Billing/Invoice question"),
        (2, "WhatsApp - Technical (app crash)"),
        (5, "Web Form - Feedback (feature request)"),
        (12, "Email - Positive feedback"),
        (18, "Email - GDPR/Legal request"),
        (20, "WhatsApp - Low sentiment (0.2)"),
        (30, "Email - Security breach (CRITICAL)"),
        (33, "Web Form - General (data residency)"),
        (40, "WhatsApp - Pricing inquiry (student discount)"),
        (54, "Email - Legal threat (CRITICAL)"),
    ]
    
    results = {
        'email': {'total': 0, 'escalated': 0},
        'whatsapp': {'total': 0, 'escalated': 0},
        'web_form': {'total': 0, 'escalated': 0},
    }
    
    for idx, description in test_cases:
        if idx >= len(tickets):
            continue
        
        ticket = tickets[idx]
        channel = ticket['channel']
        results[channel]['total'] += 1
        
        print(f"\n{'='*70}")
        print(f"TEST: {description}")
        print(f"Ticket #{ticket['id']} | Channel: {channel} | Sentiment: {ticket['sentiment']}")
        print(f"{'='*70}")
        
        # Create message
        message = CustomerMessage(
            channel=Channel(channel),
            message=ticket['message'],
            subject=ticket.get('subject'),
        )
        
        # Show message preview
        preview = message.message[:100].replace('\n', ' ')
        print(f"\n📩 Message: {preview}...")
        
        # Process
        response = agent.process_message(message)
        
        # Show response
        print(f"\n🤖 Response ({len(response.response)} chars):")
        print("-" * 50)
        print(response.response)
        print("-" * 50)
        
        # Show analysis
        status = "✓ ESCALATED" if response.escalation_needed else "✓ Resolved by AI"
        print(f"\n📊 Status: {status}")
        if response.escalation_needed:
            print(f"   Reason: {response.escalation_reason}")
            print(f"   Team: {response.escalation_team}")
            results[channel]['escalated'] += 1
        
        print()
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"{'Channel':<15} {'Total':<10} {'Escalated':<12} {'AI Resolved':<12} {'Escalation %':<12}")
    print("-" * 61)
    
    total_all = 0
    escalated_all = 0
    
    for channel, stats in results.items():
        total = stats['total']
        escalated = stats['escalated']
        resolved = total - escalated
        pct = (escalated / total * 100) if total > 0 else 0
        print(f"{channel:<15} {total:<10} {escalated:<12} {resolved:<12} {pct:.1f}%")
        total_all += total
        escalated_all += escalated
    
    print("-" * 61)
    overall_pct = (escalated_all / total_all * 100) if total_all > 0 else 0
    print(f"{'OVERALL':<15} {total_all:<10} {escalated_all:<12} {total_all - escalated_all:<12} {overall_pct:.1f}%")
    print("=" * 70)
    
    # Channel format verification
    print("\n" + "=" * 70)
    print("CHANNEL FORMAT VERIFICATION")
    print("=" * 70)
    
    # Test each channel format explicitly
    test_messages = [
        (Channel.EMAIL, "I have a question about my bill", "john.doe@example.com"),
        (Channel.WHATSAPP, "app not working send help", None),
        (Channel.WEB_FORM, "How do I export my data?", "jane@example.com"),
    ]
    
    for channel, msg, email in test_messages:
        message = CustomerMessage(
            channel=channel,
            message=msg,
            customer_email=email
        )
        response = agent.process_message(message)
        
        print(f"\n{channel.value.upper()}:")
        print(f"  Response length: {len(response.response)} chars")
        if channel == Channel.WHATSAPP:
            under_limit = len(response.response) <= 300
            print(f"  Under 300 chars: {'✓ Yes' if under_limit else '✗ No'}")
        if channel == Channel.EMAIL:
            has_greeting = response.response.startswith("Dear")
            has_signature = "Best regards," in response.response
            print(f"  Has 'Dear' greeting: {'✓ Yes' if has_greeting else '✗ No'}")
            print(f"  Has signature: {'✓ Yes' if has_signature else '✗ No'}")


if __name__ == "__main__":
    run_extended_tests()
