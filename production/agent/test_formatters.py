"""Test the production formatters module."""

import sys
sys.path.insert(0, 'production')

from agent.formatters import format_for_channel, get_channel_limits, validate_response_length

def test_all_channels():
    """Test formatting for all three channels."""
    
    print("=" * 70)
    print("Production Formatters Test")
    print("=" * 70)
    
    test_content = """To reset your password, please follow these steps:
1. Go to techcorp.com/login
2. Click "Forgot Password?"
3. Enter your email address
4. Check your inbox for the reset link (valid for 1 hour)

If you don't receive the email within 5 minutes, please check your spam folder.
For more help, visit help.techcorp.com"""
    
    # Test Email
    print("\n" + "=" * 70)
    print("EMAIL FORMAT")
    print("=" * 70)
    email_response = format_for_channel(
        test_content, 
        "email", 
        customer_name="John Doe",
        ticket_id="TKT-2025-001"
    )
    print(email_response)
    print(f"\nLength: {len(email_response)} chars, {len(email_response.split())} words")
    valid, msg = validate_response_length(email_response, "email")
    print(f"Validation: {msg}")
    
    # Test WhatsApp
    print("\n" + "=" * 70)
    print("WHATSAPP FORMAT")
    print("=" * 70)
    whatsapp_response = format_for_channel(
        test_content,
        "whatsapp",
        customer_name="John Doe",
        ticket_id="TKT-2025-001"
    )
    print(whatsapp_response)
    print(f"\nLength: {len(whatsapp_response)} chars")
    valid, msg = validate_response_length(whatsapp_response, "whatsapp")
    print(f"Validation: {msg}")
    
    # Test Web Form
    print("\n" + "=" * 70)
    print("WEB FORM FORMAT")
    print("=" * 70)
    webform_response = format_for_channel(
        test_content,
        "web_form",
        customer_name="John Doe",
        ticket_id="TKT-2025-001"
    )
    print(webform_response)
    print(f"\nLength: {len(webform_response)} chars, {len(webform_response.split())} words")
    valid, msg = validate_response_length(webform_response, "web_form")
    print(f"Validation: {msg}")
    
    # Test channel limits
    print("\n" + "=" * 70)
    print("CHANNEL LIMITS REFERENCE")
    print("=" * 70)
    for channel in ["email", "whatsapp", "web_form"]:
        limits = get_channel_limits(channel)
        print(f"\n{channel.upper()}:")
        for key, value in limits.items():
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 70)
    print("All tests complete!")
    print("=" * 70)


if __name__ == "__main__":
    test_all_channels()
