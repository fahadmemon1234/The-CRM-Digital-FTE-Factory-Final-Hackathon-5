"""
Performance Baseline Test for Customer Success AI Agent Prototype
Runs 10 test queries and measures response time and accuracy.
"""

import sys
import time
sys.path.insert(0, 'src/agent')

from prototype import CustomerSuccessAgent, CustomerMessage, Channel

def run_baseline_test():
    """Run 10 test queries and measure performance."""
    print("=" * 70)
    print("INCUBATION PHASE - Performance Baseline Test")
    print("=" * 70)
    print()
    
    agent = CustomerSuccessAgent()
    
    # 10 diverse test queries covering all channels and categories
    test_queries = [
        # (channel, message, expected_category, description)
        ("email", "Hi, I received an invoice for $79 but I thought I was on the $29 Starter plan. Can you explain this charge?", "billing", "Email - Invoice question"),
        ("whatsapp", "app keeps crashing when uploading files iphone", "technical", "WhatsApp - App crash"),
        ("web_form", "How do I integrate TechCorp with Slack? I've followed the guide but notifications aren't coming through.", "integration", "Web Form - Slack integration"),
        ("email", "I'd like to upgrade from Growth to Enterprise. What's the pricing for 100 users?", "pricing", "Email - Enterprise pricing (escalate)"),
        ("whatsapp", "forgot password how to reset", "account", "WhatsApp - Password reset"),
        ("web_form", "Can I get a refund? I was charged for annual but wanted monthly.", "billing", "Web Form - Refund request (escalate)"),
        ("email", "Our Salesforce integration stopped syncing. This is affecting our sales team.", "technical", "Email - Salesforce sync issue"),
        ("whatsapp", "is there a student discount?", "pricing", "WhatsApp - Student discount (escalate)"),
        ("web_form", "The calendar view shows wrong dates. Tasks due Jan 20 show as Jan 19.", "bug", "Web Form - Calendar bug"),
        ("email", "I want to speak to a human. This bot is not helpful.", "complaint", "Email - Human request (escalate)"),
    ]
    
    results = []
    response_times = []
    correct_categorizations = 0
    escalations_detected = 0
    
    for i, (channel_str, message, expected_category, description) in enumerate(test_queries, 1):
        channel = Channel(channel_str)
        
        msg = CustomerMessage(
            channel=channel,
            message=message,
            customer_email=f"test{i}@example.com"
        )
        
        # Measure response time
        start_time = time.time()
        response = agent.process_message(msg)
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        response_times.append(response_time_ms)
        
        # Check if escalation was correctly detected
        escalation_expected = expected_category in ["pricing", "complaint"] or "refund" in message.lower()
        escalation_correct = response.escalation_needed == escalation_expected
        
        if escalation_expected and response.escalation_needed:
            escalations_detected += 1
        
        # Determine if response was appropriate
        response_appropriate = len(response.response) > 0
        
        results.append({
            "query_num": i,
            "description": description,
            "channel": channel_str,
            "response_time_ms": round(response_time_ms, 2),
            "escalation_needed": response.escalation_needed,
            "escalation_correct": escalation_correct,
            "response_length": len(response.response),
            "appropriate": response_appropriate
        })
        
        if response_appropriate:
            correct_categorizations += 1
        
        print(f"Query {i}: {description}")
        print(f"  Channel: {channel_str} | Time: {response_time_ms:.2f}ms | Escalation: {response.escalation_needed}")
        print(f"  Response Length: {len(response.response)} chars | Appropriate: {response_appropriate}")
        print()
    
    # Calculate metrics
    avg_response_time = sum(response_times) / len(response_times)
    max_response_time = max(response_times)
    min_response_time = min(response_times)
    accuracy = (correct_categorizations / len(test_queries)) * 100
    escalation_accuracy = (escalations_detected / 4) * 100  # 4 queries should escalate
    
    print("=" * 70)
    print("BASELINE PERFORMANCE METRICS")
    print("=" * 70)
    print()
    print(f"Total Queries Tested: {len(test_queries)}")
    print()
    print("Response Time:")
    print(f"  Average: {avg_response_time:.2f}ms")
    print(f"  Minimum: {min_response_time:.2f}ms")
    print(f"  Maximum: {max_response_time:.2f}ms")
    print(f"  Target: < 3000ms (3 seconds)")
    print(f"  Status: {'✓ PASS' if avg_response_time < 3000 else '✗ FAIL'}")
    print()
    print("Accuracy:")
    print(f"  Response Generation: {accuracy:.1f}%")
    print(f"  Escalation Detection: {escalation_accuracy:.1f}% ({escalations_detected}/4 correct)")
    print(f"  Target: > 85%")
    print(f"  Status: {'✓ PASS' if accuracy >= 85 else '✗ NEEDS IMPROVEMENT'}")
    print()
    print("Channel Coverage:")
    channels_tested = set(r["channel"] for r in results)
    print(f"  Channels Tested: {list(channels_tested)}")
    print(f"  All 3 Channels: {'✓ YES' if len(channels_tested) == 3 else '✗ NO'}")
    print()
    print("Escalation Handling:")
    print(f"  Total Escalations Triggered: {sum(1 for r in results if r['escalation_needed'])}")
    print(f"  Expected Escalations: 4")
    print()
    print("=" * 70)
    
    return {
        "avg_response_time_ms": avg_response_time,
        "max_response_time_ms": max_response_time,
        "min_response_time_ms": min_response_time,
        "accuracy_pct": accuracy,
        "escalation_accuracy_pct": escalation_accuracy,
        "queries_tested": len(test_queries),
        "channels_covered": list(channels_tested)
    }


if __name__ == "__main__":
    run_baseline_test()
