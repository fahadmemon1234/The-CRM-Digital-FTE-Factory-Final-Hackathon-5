"""
Test WhatsApp webhook flow end-to-end
"""
import requests

# Test webhook endpoint
print("Testing WhatsApp webhook...")
response = requests.post(
    "http://localhost:8000/webhooks/whatsapp",
    data={
        "From": "whatsapp:+923153268177",
        "Body": "Automated test message",
        "MessageSid": "SMautotest123"
    }
)

print(f"Response: {response.json()}")
print(f"Status Code: {response.status_code}")

if response.json().get("status") == "received":
    print("✅ Webhook test PASSED!")
    print(f"   Ticket ID: {response.json().get('ticket_id')}")
else:
    print("❌ Webhook test FAILED!")
    print(f"   Error: {response.json().get('message', 'Unknown error')}")
