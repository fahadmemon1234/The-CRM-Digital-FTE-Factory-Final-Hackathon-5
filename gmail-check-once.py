"""
Gmail One-Time Checker - Check Gmail for unread emails and create tickets
"""

import os
import sys
import base64
import requests
from datetime import datetime
from dotenv import load_dotenv
from google.oauth2 import credentials
from googleapiclient.discovery import build

# Load environment variables
load_dotenv("production/.env")

# Configuration
WEBHOOK_URL = "http://localhost:8000/webhooks/email"

def get_gmail_service():
    """Initialize Gmail API service"""
    client_id = os.getenv('GMAIL_CLIENT_ID')
    client_secret = os.getenv('GMAIL_CLIENT_SECRET')
    refresh_token = os.getenv('GMAIL_REFRESH_TOKEN')
    
    if not all([client_id, client_secret, refresh_token]):
        print("❌ Gmail credentials not configured!")
        return None
    
    creds = credentials.Credentials(
        None,
        client_id=client_id,
        client_secret=client_secret,
        token_uri="https://oauth2.googleapis.com/token",
        refresh_token=refresh_token
    )
    
    service = build('gmail', 'v1', credentials=creds)
    return service

def get_unread_messages(service, user_id='me'):
    """Get list of unread messages"""
    try:
        results = service.users().messages().list(
            userId=user_id,
            q='is:unread',
            maxResults=10
        ).execute()
        
        messages = results.get('messages', [])
        return messages
    except Exception as e:
        print(f"Error fetching messages: {e}")
        return []

def get_message_details(service, user_id, msg_id):
    """Get full message details"""
    try:
        message = service.users().messages().get(
            userId=user_id,
            id=msg_id,
            format='full'
        ).execute()
        
        # Extract headers
        headers = message.get('payload', {}).get('headers', [])
        from_email = ''
        subject = ''
        
        for header in headers:
            if header['name'] == 'From':
                from_email = header['value']
            elif header['name'] == 'Subject':
                subject = header['value']
        
        # Extract body
        body = ''
        payload = message.get('payload', {})
        
        if 'parts' in payload:
            # Multipart email
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    body_data = part.get('body', {}).get('data', '')
                    if body_data:
                        body = base64.urlsafe_b64decode(body_data).decode('utf-8')
                        break
        else:
            # Simple email
            body_data = payload.get('body', {}).get('data', '')
            if body_data:
                body = base64.urlsafe_b64decode(body_data).decode('utf-8')
        
        return {
            'id': msg_id,
            'from': from_email,
            'subject': subject,
            'body': body,
            'thread_id': message.get('threadId', '')
        }
        
    except Exception as e:
        print(f"Error fetching message {msg_id}: {e}")
        return None

def mark_as_read(service, user_id, msg_id):
    """Mark message as read"""
    try:
        service.users().messages().modify(
            userId=user_id,
            id=msg_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        print(f"   ✓ Marked as read")
    except Exception as e:
        print(f"Error marking as read: {e}")

def send_to_webhook(email_data):
    """Send email data to webhook"""
    try:
        print(f"   → Sending to webhook...")
        response = requests.post(
            WEBHOOK_URL,
            json={
                'from': email_data['from'],
                'subject': email_data['subject'],
                'body': email_data['body'],
                'message_id': email_data['id']
            },
            timeout=10
        )
        
        result = response.json()
        
        if result.get('status') == 'received':
            print(f"   ✓ Ticket created: {result.get('ticket_id')}")
            return True
        else:
            print(f"   ✗ Webhook error: {result}")
            return False
            
    except Exception as e:
        print(f"   ✗ Webhook connection error: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("Gmail One-Time Checker - Ticket Creator")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    service = get_gmail_service()
    
    if not service:
        print("❌ Failed to initialize Gmail service")
        return
    
    print("✅ Gmail connected successfully!")
    print("\nSearching for unread emails...\n")
    
    # Get unread messages
    messages = get_unread_messages(service)
    
    if messages:
        print(f"📬 Found {len(messages)} unread email(s)!\n")
        
        for msg in messages:
            msg_id = msg['id']
            
            # Get message details
            email_data = get_message_details(service, 'me', msg_id)
            
            if email_data and email_data['body']:
                print(f"📧 Processing email:")
                print(f"   From: {email_data['from']}")
                print(f"   Subject: {email_data['subject']}")
                # Print body safely (handle Unicode)
                body_preview = email_data['body'][:100].encode('ascii', 'ignore').decode('ascii')
                print(f"   Body: {body_preview}...")
                
                # Send to webhook
                if send_to_webhook(email_data):
                    # Mark as read
                    mark_as_read(service, 'me', msg_id)
                
                print()
    else:
        print("📭 No unread emails found.")
        print("\n💡 Tip: Send an email to fahadgraphicx11@gmail.com to test!")
    
    print("=" * 60)
    print("Done!")
    print("=" * 60)

if __name__ == "__main__":
    main()
