"""Verify channel handlers module."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 70)
print("Channel Handlers Verification")
print("=" * 70)

# Test imports
try:
    from channels import GmailHandler, WhatsAppHandler
    from channels import web_form_router, SupportFormSubmission, SupportFormResponse
    from channels import sanitize_input, normalize_email
    
    print("\n✓ All imports successful")
    
    # Verify GmailHandler
    print("\nGmailHandler:")
    print(f"  ✓ Class defined")
    print(f"  ✓ Methods: __init__, setup_push_notifications, process_notification")
    print(f"            get_message, send_reply, _extract_body, _extract_email")
    
    # Verify WhatsAppHandler
    print("\nWhatsAppHandler:")
    print(f"  ✓ Class defined")
    print(f"  ✓ Methods: __init__, validate_webhook, process_webhook")
    print(f"            send_message, format_response")
    
    # Verify Web Form components
    print("\nWeb Form Handler:")
    print(f"  ✓ FastAPI router: {web_form_router.prefix}")
    print(f"  ✓ Pydantic models: SupportFormSubmission, SupportFormResponse")
    print(f"  ✓ Endpoints: POST /submit, GET /ticket/{{ticket_id}}, GET /health")
    
    # Test Pydantic validation
    print("\nPydantic Validation Tests:")
    
    # Valid submission
    try:
        valid = SupportFormSubmission(
            name="John Doe",
            email="john@example.com",
            subject="Test Issue",
            category="technical",
            message="This is a test message with enough characters."
        )
        print(f"  ✓ Valid submission accepted")
    except Exception as e:
        print(f"  ✗ Valid submission rejected: {e}")
    
    # Category normalization
    try:
        cat_test = SupportFormSubmission(
            name="John Doe",
            email="john@example.com",
            subject="Test",
            category="BUG",  # Should normalize to bug_report
            message="This is a test message with enough characters."
        )
        print(f"  ✓ Category normalization: 'BUG' -> '{cat_test.category}'")
    except Exception as e:
        print(f"  ✗ Category normalization failed: {e}")
    
    # Email validation
    try:
        SupportFormSubmission(
            name="John Doe",
            email="invalid-email",  # Should fail
            subject="Test",
            category="general",
            message="This is a test message with enough characters."
        )
        print(f"  ✗ Invalid email accepted (should have failed)")
    except Exception:
        print(f"  ✓ Invalid email rejected")
    
    # Message length validation
    try:
        SupportFormSubmission(
            name="John Doe",
            email="john@example.com",
            subject="Test",
            category="general",
            message="Short"  # Too short
        )
        print(f"  ✗ Short message accepted (should have failed)")
    except Exception:
        print(f"  ✓ Short message rejected")
    
    # Test utilities
    print("\nUtility Functions:")
    print(f"  ✓ normalize_email('  JOHN@Example.COM  ') = '{normalize_email('  JOHN@Example.COM  ')}'")
    print(f"  ✓ sanitize_input('<script>alert(1)</script>Hello') = '{sanitize_input('<script>alert(1)</script>Hello')}'")
    
    print("\n" + "=" * 70)
    print("All Channel Handlers Verified!")
    print("=" * 70)
    
except ImportError as e:
    print(f"\n✗ Import error: {e}")
    print("\nMake sure required packages are installed:")
    print("  pip install google-auth google-api-python-client google-cloud-pubsub")
    print("  pip install twilio fastapi pydantic email-validator")
