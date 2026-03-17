"""
Test complete email webhook flow
"""
import requests
import json

print("Testing Email Webhook Flow...")
print("=" * 60)

# Test 1: Send email webhook
print("\n1. Sending email webhook...")
response = requests.post(
    "http://localhost:8000/webhooks/email",
    json={
        "from": "fahadgraphicx11@gmail.com",
        "subject": "Test Email - Order Issue",
        "body": "Hello, I need help with my order #12345. It hasn't arrived yet.",
        "message_id": "test-email-001"
    }
)

print(f"   Response: {response.json()}")
print(f"   Status Code: {response.status_code}")

if response.json().get("status") == "received":
    print("   ✅ Email webhook test PASSED!")
    print(f"   Ticket ID: {response.json().get('ticket_id')}")
else:
    print("   ❌ Email webhook test FAILED!")
    print(f"   Error: {response.json().get('message', 'Unknown')}")

print("\n" + "=" * 60)
print("Check your Gmail inbox for auto-reply!")
