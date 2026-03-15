"""
TechCorp Customer Success AI Agent - WhatsApp Channel Handler

Handles inbound and outbound WhatsApp communication via Twilio API.

INCUBATION MAPPING:
-------------------
Incubation: No WhatsApp integration (simulated in prototype.py)
Production: Full Twilio WhatsApp Business API integration

Key Features:
- Twilio webhook validation for security
- Real-time message processing via webhooks
- Message splitting for long responses
- Delivery status tracking
- Profile information extraction

Author: AI Engineering Team
Version: 1.0.0 (Production)
"""

import os
import re
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any

from twilio.rest import Client
from twilio.request_validator import RequestValidator
from fastapi import Request, HTTPException, Form

logger = logging.getLogger(__name__)


class WhatsAppHandler:
    """
    WhatsApp channel handler for customer support messages.
    
    INCUBATION EQUIVALENT: No WhatsApp handling (simulated)
    PRODUCTION: Full Twilio WhatsApp Business API integration
    
    Authentication:
    - Twilio Account SID and Auth Token
    - Webhook signature validation
    
    Usage:
        handler = WhatsAppHandler()
        
        # Validate incoming webhook
        is_valid = await handler.validate_webhook(request)
        
        # Process webhook
        message = await handler.process_webhook(form_data)
        
        # Send message
        result = await handler.send_message(
            to_phone="+1234567890",
            body="Hello from TechCorp!"
        )
    """
    
    # WhatsApp channel identifier
    CHANNEL = 'whatsapp'
    
    # Max message length for WhatsApp (1600 chars for Business API)
    MAX_MESSAGE_LENGTH = 1600
    
    def __init__(self):
        """
        Initialize WhatsApp handler with Twilio credentials.
        
        INCUBATION: No credentials (simulated)
        PRODUCTION: Twilio Account SID and Auth Token from environment
        """
        # Load credentials from environment
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')
        
        if not all([self.account_sid, self.auth_token, self.whatsapp_number]):
            logger.warning(
                "Twilio credentials not fully configured. "
                "Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER"
            )
        
        # Initialize Twilio client
        self.client = Client(self.account_sid, self.auth_token) if self.account_sid else None
        
        # Initialize request validator
        self.validator = RequestValidator(self.auth_token) if self.auth_token else None
        
        logger.info("WhatsAppHandler initialized")
    
    async def validate_webhook(self, request: Request) -> bool:
        """
        Validate Twilio webhook signature for security.
        
        INCUBATION: No validation (simulated)
        PRODUCTION: Twilio RequestValidator signature check
        
        Args:
            request: FastAPI Request object
            
        Returns:
            True if signature is valid
            
        Raises:
            HTTPException: If signature validation fails
        """
        if not self.validator:
            logger.warning("Twilio validator not configured, skipping validation")
            return True
        
        try:
            # Get the request body as string
            body = await request.body()
            body_string = body.decode('utf-8') if body else ''
            
            # Get the signature from headers
            signature = request.headers.get('X-Twilio-Signature', '')
            
            # Get the request URL
            url = str(request.url)
            
            # Validate signature
            is_valid = self.validator.validate(
                url=url,
                params=body_string,
                signature=signature
            )
            
            if not is_valid:
                logger.warning(f"Invalid Twilio signature from {request.client.host}")
                raise HTTPException(
                    status_code=403,
                    detail="Invalid webhook signature"
                )
            
            logger.info("Webhook signature validated")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error validating webhook: {e}")
            raise HTTPException(status_code=500, detail="Webhook validation error")
    
    async def process_webhook(self, form_data: dict) -> Optional[Dict[str, Any]]:
        """
        Parse Twilio webhook form data into standardized message format.
        
        INCUBATION: Simulated message dict
        PRODUCTION: Twilio webhook parsing with full metadata
        
        Args:
            form_data: Twilio webhook form data (application/x-www-form-urlencoded)
            
        Returns:
            Dict with channel, channel_message_id, customer_phone, content,
            received_at, metadata
        """
        try:
            # Extract message data from Twilio webhook
            message_sid = form_data.get('MessageSid', '')
            from_number = form_data.get('From', '')
            body = form_data.get('Body', '')
            num_media = form_data.get('NumMedia', '0')
            profile_name = form_data.get('ProfileName', '')
            wa_id = form_data.get('WaId', '')
            sms_status = form_data.get('SmsStatus', 'received')
            
            # Clean phone number (remove "whatsapp:" prefix)
            customer_phone = from_number.replace('whatsapp:', '') if from_number else ''
            
            # Build metadata
            metadata = {
                'twilio_message_sid': message_sid,
                'from_number': from_number,
                'num_media': int(num_media) if num_media.isdigit() else 0,
                'profile_name': profile_name,
                'wa_id': wa_id,
                'sms_status': sms_status,
                'raw_form_data': form_data
            }
            
            # Check for media attachments
            if int(num_media) > 0:
                media_urls = []
                for i in range(int(num_media)):
                    media_url = form_data.get(f'MediaUrl{i}', '')
                    media_type = form_data.get(f'MediaContentType{i}', '')
                    if media_url:
                        media_urls.append({'url': media_url, 'type': media_type})
                metadata['media'] = media_urls
            
            message_data = {
                'channel': self.CHANNEL,
                'channel_message_id': message_sid,
                'customer_phone': customer_phone,
                'content': body,
                'received_at': datetime.utcnow().isoformat(),
                'metadata': metadata
            }
            
            logger.info(f"Processed WhatsApp message from {customer_phone}")
            return message_data
            
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return None
    
    async def send_message(self, to_phone: str, body: str) -> Dict[str, Any]:
        """
        Send WhatsApp message via Twilio API.
        
        INCUBATION: Simulated send (print statement)
        PRODUCTION: Twilio API send with delivery confirmation
        
        Args:
            to_phone: Recipient phone number
            body: Message body content
            
        Returns:
            Dict with channel_message_id and delivery_status
        """
        if not self.client:
            logger.error("Twilio client not initialized")
            return {
                'channel_message_id': None,
                'delivery_status': 'failed',
                'error': 'Twilio client not initialized'
            }
        
        try:
            # Ensure phone number has whatsapp: prefix
            if not to_phone.startswith('whatsapp:'):
                to_phone = f'whatsapp:{to_phone}'
            
            # Ensure sender has whatsapp: prefix
            from_number = self.whatsapp_number
            if not from_number.startswith('whatsapp:'):
                from_number = f'whatsapp:{from_number}'
            
            # Send message via Twilio
            message = self.client.messages.create(
                body=body,
                from_=from_number,
                to=to_phone
            )
            
            logger.info(f"WhatsApp message sent to {to_phone}, SID: {message.sid}")
            
            return {
                'channel_message_id': message.sid,
                'delivery_status': 'sent',
                'sent_at': datetime.utcnow().isoformat(),
                'to_phone': to_phone
            }
            
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {e}")
            return {
                'channel_message_id': None,
                'delivery_status': 'failed',
                'error': str(e)
            }
    
    def format_response(self, response: str, max_length: int = 1600) -> List[str]:
        """
        Split long messages at sentence boundaries for WhatsApp.
        
        INCUBATION: Simple truncation with "..."
        PRODUCTION: Intelligent sentence-boundary splitting
        
        Args:
            response: Full response text
            max_length: Maximum characters per message (default 1600)
            
        Returns:
            List of message chunks
        """
        if len(response) <= max_length:
            return [response]
        
        chunks = []
        remaining = response
        
        while len(remaining) > max_length:
            # Find last sentence boundary within limit
            cut_point = max_length
            
            # Try to find sentence ending (., !, ?) followed by space
            for punct in ['.', '!', '?']:
                last_punct = remaining[:max_length].rfind(punct)
                if last_punct > max_length // 2:  # At least halfway through
                    cut_point = last_punct + 1
                    break
            
            # If no sentence boundary found, try newline
            if cut_point == max_length:
                last_newline = remaining[:max_length].rfind('\n')
                if last_newline > max_length // 2:
                    cut_point = last_newline
            
            # Extract chunk
            chunk = remaining[:cut_point].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move to remaining text
            remaining = remaining[cut_point:].strip()
        
        # Add final chunk
        if remaining:
            chunks.append(remaining)
        
        logger.info(f"Split message into {len(chunks)} chunks")
        return chunks
    
    async def send_split_message(self, to_phone: str, body: str) -> List[Dict[str, Any]]:
        """
        Send long message as multiple WhatsApp messages.
        
        Args:
            to_phone: Recipient phone number
            body: Full message body
            
        Returns:
            List of send results for each chunk
        """
        chunks = self.format_response(body)
        results = []
        
        for i, chunk in enumerate(chunks):
            # Add continuation indicator for multi-part messages
            if len(chunks) > 1:
                prefix = f"({i+1}/{len(chunks)}) "
                chunk = prefix + chunk
            
            result = await self.send_message(to_phone, chunk)
            results.append(result)
            
            # Small delay between messages to avoid rate limiting
            if i < len(chunks) - 1:
                import asyncio
                await asyncio.sleep(0.5)
        
        return results
    
    async def get_message_status(self, message_sid: str) -> Optional[str]:
        """
        Get delivery status of a sent message.
        
        Args:
            message_sid: Twilio message SID
            
        Returns:
            Status string: queued, sent, delivered, failed, or None
        """
        if not self.client:
            return None
        
        try:
            message = self.client.messages(message_sid).fetch()
            return message.status
        except Exception as e:
            logger.error(f"Error fetching message status: {e}")
            return None
    
    async def close(self):
        """Clean up resources."""
        if self.client:
            # Twilio client doesn't have explicit close method
            pass
        logger.info("WhatsAppHandler closed")
