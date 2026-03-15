"""
TechCorp Customer Success AI Agent - Gmail Channel Handler

Handles inbound and outbound email communication via Gmail API.

INCUBATION MAPPING:
-------------------
Incubation: No email integration (simulated in prototype.py)
Production: Full Gmail API integration with OAuth2 and Pub/Sub notifications

Key Features:
- OAuth2 authentication with Google
- Pub/Sub push notifications for real-time email processing
- Multipart email parsing (plain text and HTML)
- Thread-aware reply handling
- Delivery status tracking

Author: AI Engineering Team
Version: 1.0.0 (Production)
"""

import os
import re
import json
import base64
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
from email.mime.text import MIMEText

from google.oauth2 import credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.cloud import pubsub_v1

logger = logging.getLogger(__name__)


class GmailHandler:
    """
    Gmail channel handler for customer support emails.
    
    INCUBATION EQUIVALENT: No email handling (simulated)
    PRODUCTION: Full Gmail API integration
    
    Authentication:
    - Service account for sending emails
    - OAuth2 credentials for receiving emails
    - Pub/Sub for push notifications
    
    Usage:
        handler = GmailHandler("path/to/credentials.json")
        await handler.setup_push_notifications("gmail-notifications")
        
        # Process incoming notification
        messages = await handler.process_notification(pubsub_message)
        
        # Send reply
        result = await handler.send_reply(
            to_email="customer@example.com",
            subject="Re: Your ticket",
            body="Hello...",
            thread_id="thread_123"
        )
    """
    
    # Gmail API scopes
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    def __init__(self, credentials_path: str):
        """
        Initialize Gmail handler with OAuth credentials.
        
        INCUBATION: No credentials (simulated)
        PRODUCTION: Service account OAuth credentials
        
        Args:
            credentials_path: Path to Google service account JSON credentials
        """
        self.credentials_path = credentials_path
        self.service = None
        self.pubsub_client = None
        self.project_id = None
        self.history_id = None
        
        # Load credentials and build service
        self._initialize_service()
        
        # Get project ID for Pub/Sub
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        
        logger.info("GmailHandler initialized")
    
    def _initialize_service(self):
        """Initialize Gmail API service with credentials."""
        try:
            # Check if credentials file exists and has content
            if not os.path.exists(self.credentials_path):
                raise FileNotFoundError(f"Credentials file not found: {self.credentials_path}")
            
            # Validate credentials file has required fields
            import json
            with open(self.credentials_path, 'r') as f:
                creds_data = json.load(f)
            
            # Check for required service account fields
            required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email', 'client_id']
            missing_fields = [f for f in required_fields if f not in creds_data]
            if missing_fields:
                raise ValueError(f"Credentials file missing required fields: {missing_fields}")
            
            # Load service account credentials
            creds = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=self.SCOPES
            )

            # Build Gmail API service
            self.service = build('gmail', 'v1', credentials=creds)

            # Get initial history ID for incremental fetch
            profile = self.service.users().getProfile(userId='me').execute()
            self.history_id = profile.get('historyId')

            logger.info(f"Gmail service initialized, historyId: {self.history_id}")

        except FileNotFoundError as e:
            logger.error(f"Credentials file not found: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in credentials file: {e}")
            raise
        except ValueError as e:
            logger.error(f"Invalid credentials format: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Gmail service: {e}")
            raise
    
    async def setup_push_notifications(self, topic_name: str) -> str:
        """
        Set up Gmail Pub/Sub watch on INBOX for real-time notifications.
        
        INCUBATION: No push notifications (polling simulation)
        PRODUCTION: Gmail Pub/Sub integration for instant notifications
        
        Args:
            topic_name: Pub/Sub topic name (e.g., "gmail-notifications")
            
        Returns:
            Topic full name
            
        Raises:
            RuntimeError: If project_id not configured
        """
        if not self.project_id:
            raise RuntimeError("GOOGLE_CLOUD_PROJECT environment variable not set")
        
        try:
            # Initialize Pub/Sub client
            self.pubsub_client = pubsub_v1.PublisherClient()
            
            # Create or get topic
            topic_full_name = f"projects/{self.project_id}/topics/{topic_name}"
            
            try:
                self.pubsub_client.get_topic(request={"topic": topic_full_name})
                logger.info(f"Topic exists: {topic_full_name}")
            except Exception:
                # Create topic if not exists
                self.pubsub_client.create_topic(request={"name": topic_full_name})
                logger.info(f"Created topic: {topic_full_name}")
            
            # Create subscription
            subscription_name = f"gmail-subscription"
            subscription_full_name = f"projects/{self.project_id}/subscriptions/{subscription_name}"
            
            try:
                self.pubsub_client.get_subscription(
                    request={"subscription": subscription_full_name}
                )
            except Exception:
                # Create subscription with ack deadline
                self.pubsub_client.create_subscription(
                    request={
                        "name": subscription_full_name,
                        "topic": topic_full_name,
                        "ack_deadline_seconds": 30
                    }
                )
                logger.info(f"Created subscription: {subscription_full_name}")
            
            # Set up Gmail watch
            watch_request = {
                'topicName': topic_full_name,
                'labelIds': ['INBOX']  # Only watch INBOX
            }
            
            watch_response = self.service.users().watch(
                userId='me',
                body=watch_request
            ).execute()
            
            new_history_id = watch_response.get('historyId')
            logger.info(f"Gmail watch set up, new historyId: {new_history_id}")
            self.history_id = new_history_id
            
            return topic_full_name
            
        except HttpError as e:
            logger.error(f"Gmail API error setting up watch: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to set up push notifications: {e}")
            raise
    
    async def process_notification(self, pubsub_message: dict) -> List[Dict[str, Any]]:
        """
        Process Pub/Sub notification and fetch new messages.
        
        INCUBATION: No notifications (simulated polling)
        PRODUCTION: Incremental fetch based on historyId
        
        Args:
            pubsub_message: Pub/Sub message data
            
        Returns:
            List of parsed message dicts
        """
        try:
            # Get history since last check
            history_response = self.service.users().history().list(
                userId='me',
                startHistoryId=self.history_id,
                historyTypes=['messageAdded']
            ).execute()
            
            history_records = history_response.get('history', [])
            messages_to_process = []
            
            for history_record in history_records:
                messages_added = history_record.get('messagesAdded', [])
                for message_event in messages_added:
                    message_data = message_event.get('message', {})
                    message_id = message_data.get('id')
                    
                    if message_id:
                        # Fetch full message
                        message = await self.get_message(message_id)
                        if message:
                            messages_to_process.append(message)
                    
                    # Update history ID
                    self.history_id = history_record.get('id', self.history_id)
            
            logger.info(f"Processed {len(messages_to_process)} new messages")
            return messages_to_process
            
        except HttpError as e:
            if e.resp.status == 404:
                # History expired, reset to current
                logger.warning("Gmail history expired, resetting")
                profile = self.service.users().getProfile(userId='me').execute()
                self.history_id = profile.get('historyId')
                return []
            logger.error(f"Error processing notification: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to process notification: {e}")
            return []
    
    async def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch and parse full Gmail message.
        
        INCUBATION: Simulated message dict
        PRODUCTION: Gmail API fetch with full parsing
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            Dict with channel, channel_message_id, customer_email, subject,
            content, received_at, thread_id, metadata
        """
        try:
            # Fetch message from Gmail API
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Parse headers
            headers = message.get('payload', {}).get('headers', [])
            header_dict = {h['name']: h['value'] for h in headers}
            
            # Extract email from From header
            from_header = header_dict.get('From', '')
            customer_email = self._extract_email(from_header)
            
            # Extract subject
            subject = header_dict.get('Subject', '')
            
            # Extract received date
            date_header = header_dict.get('Date', '')
            received_at = self._parse_date(date_header)
            
            # Extract thread ID
            thread_id = message.get('threadId', '')
            
            # Extract body content
            payload = message.get('payload', {})
            content = self._extract_body(payload)
            
            # Build metadata
            metadata = {
                'gmail_message_id': message_id,
                'gmail_thread_id': thread_id,
                'from_name': header_dict.get('From', ''),
                'to': header_dict.get('To', ''),
                'cc': header_dict.get('Cc', ''),
                'labels': message.get('labelIds', []),
                'snippet': message.get('snippet', '')
            }
            
            return {
                'channel': 'email',
                'channel_message_id': message_id,
                'customer_email': customer_email,
                'subject': subject,
                'content': content,
                'received_at': received_at.isoformat() if received_at else datetime.utcnow().isoformat(),
                'thread_id': thread_id,
                'metadata': metadata
            }
            
        except HttpError as e:
            logger.error(f"Failed to fetch Gmail message {message_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing Gmail message: {e}")
            return None
    
    def _extract_body(self, payload: dict) -> str:
        """
        Extract body from email payload.
        
        INCUBATION: Simple string extraction
        PRODUCTION: Handles multipart and base64 decoding
        
        Args:
            payload: Gmail message payload dict
            
        Returns:
            Extracted body text
        """
        # Handle multipart messages
        parts = payload.get('parts', [])
        
        if parts:
            # Try to find plain text part first
            for part in parts:
                mime_type = part.get('mimeType', '')
                
                if mime_type == 'text/plain':
                    body_data = part.get('body', {}).get('data', '')
                    if body_data:
                        return base64.urlsafe_b64decode(body_data).decode('utf-8', errors='replace')
                
                # Recursively handle nested multipart
                if mime_type.startswith('multipart/'):
                    nested_body = self._extract_body(part)
                    if nested_body:
                        return nested_body
            
            # Fall back to HTML if no plain text
            for part in parts:
                if part.get('mimeType') == 'text/html':
                    body_data = part.get('body', {}).get('data', '')
                    if body_data:
                        html_content = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='replace')
                        # Strip HTML tags (simple approach)
                        return re.sub(r'<[^>]+>', '', html_content)
            
            return ""
        
        # Single part message
        body_data = payload.get('body', {}).get('data', '')
        if body_data:
            return base64.urlsafe_b64decode(body_data).decode('utf-8', errors='replace')
        
        return ""
    
    def _extract_email(self, from_header: str) -> str:
        """
        Extract email address from From header.
        
        INCUBATION: Simple string parsing
        PRODUCTION: Regex-based extraction for all formats
        
        Handles formats:
        - "email@example.com"
        - "Name <email@example.com>"
        - "Name (comment) <email@example.com>"
        
        Args:
            from_header: From header value
            
        Returns:
            Extracted email address
        """
        # Pattern to match email in angle brackets
        match = re.search(r'<([^>]+)>', from_header)
        if match:
            return match.group(1).strip()
        
        # Pattern to match bare email
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', from_header)
        if match:
            return match.group(0)
        
        # Return as-is if no match
        return from_header.strip()
    
    def _parse_date(self, date_string: str) -> Optional[datetime]:
        """Parse RFC 2822 date string to datetime."""
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_string)
        except Exception:
            return datetime.utcnow()
    
    async def send_reply(
        self,
        to_email: str,
        subject: str,
        body: str,
        thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send email reply via Gmail API.
        
        INCUBATION: Simulated send (print statement)
        PRODUCTION: Gmail API send with delivery confirmation
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            thread_id: Optional thread ID for reply threading
            
        Returns:
            Dict with channel_message_id and delivery_status
        """
        try:
            # Create MIME message
            message = MIMEText(body, 'plain', 'utf-8')
            message['to'] = to_email
            message['from'] = 'support@techcorp.com'
            message['subject'] = subject
            
            if thread_id:
                message['In-Reply-To'] = thread_id
                message['References'] = thread_id
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode('utf-8')
            
            # Send via Gmail API
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            message_id = sent_message.get('id')
            thread_id_response = sent_message.get('threadId')
            
            logger.info(f"Email sent to {to_email}, message_id: {message_id}")
            
            return {
                'channel_message_id': message_id,
                'thread_id': thread_id_response,
                'delivery_status': 'sent',
                'sent_at': datetime.utcnow().isoformat()
            }
            
        except HttpError as e:
            logger.error(f"Failed to send email: {e}")
            return {
                'channel_message_id': None,
                'delivery_status': 'failed',
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {
                'channel_message_id': None,
                'delivery_status': 'failed',
                'error': str(e)
            }
    
    async def stop_notifications(self):
        """Stop Gmail push notifications."""
        try:
            self.service.users().stop(userId='me').execute()
            logger.info("Gmail push notifications stopped")
        except Exception as e:
            logger.error(f"Error stopping notifications: {e}")
    
    async def close(self):
        """Clean up resources."""
        await self.stop_notifications()
        if self.pubsub_client:
            self.pubsub_client.transport.grpc_channel.close()
        logger.info("GmailHandler closed")
