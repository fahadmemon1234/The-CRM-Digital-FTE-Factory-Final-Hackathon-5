"""
Test Gmail API credentials
"""
import os
from dotenv import load_dotenv
from google.oauth2 import credentials
from googleapiclient.discovery import build

load_dotenv("production/.env")

# Get Gmail credentials from environment
client_id = os.getenv('GMAIL_CLIENT_ID')
client_secret = os.getenv('GMAIL_CLIENT_SECRET')
refresh_token = os.getenv('GMAIL_REFRESH_TOKEN')

print("GMAIL API TEST")
print("=" * 50)
print(f"Client ID: {client_id[:20]}...")
print(f"Client Secret: {client_secret[:10]}...")
print(f"Refresh Token: {refresh_token[:20]}...")
print()

try:
    # Create credentials from refresh token
    creds = credentials.Credentials(
        None,
        client_id=client_id,
        client_secret=client_secret,
        token_uri="https://oauth2.googleapis.com/token",
        refresh_token=refresh_token
    )
    
    # Build Gmail service
    service = build('gmail', 'v1', credentials=creds)
    
    # Get profile
    profile = service.users().getProfile(userId='me').execute()
    
    print("✅ Gmail API Connection SUCCESSFUL!")
    print(f"   Email: {profile['emailAddress']}")
    print(f"   Total Messages: {profile['messagesTotal']}")
    print(f"   Total Threads: {profile['threadsTotal']}")
    
except Exception as e:
    print(f"❌ Gmail API Connection FAILED!")
    print(f"   Error: {e}")
