"""
TechCorp Customer Success AI Agent - Channel Handlers

This package provides channel integration handlers for:
- Gmail (email)
- WhatsApp (via Twilio)
- Web Form (FastAPI REST API)

INCUBATION MAPPING:
-------------------
Incubation: Simulated channel handling in prototype.py
Production: Full channel integrations with external APIs

Package Structure:
- gmail_handler.py: Gmail API with OAuth2 and Pub/Sub
- whatsapp_handler.py: Twilio WhatsApp Business API
- web_form_handler.py: FastAPI router with Pydantic validation

Usage:
    from production.channels import GmailHandler, WhatsAppHandler
    from production.channels.web_form_handler import router as web_form_router
    
    # Initialize handlers
    gmail = GmailHandler("credentials.json")
    whatsapp = WhatsAppHandler()
    
    # Include FastAPI router
    app.include_router(web_form_router)
"""

from .gmail_handler import GmailHandler
from .whatsapp_handler import WhatsAppHandler
from .web_form_handler import (
    router as web_form_router,
    SupportFormSubmission,
    SupportFormResponse,
    TicketStatusResponse,
    sanitize_input,
    normalize_email
)

__all__ = [
    # Handlers
    'GmailHandler',
    'WhatsAppHandler',
    
    # FastAPI router
    'web_form_router',
    
    # Pydantic models
    'SupportFormSubmission',
    'SupportFormResponse',
    'TicketStatusResponse',
    
    # Utilities
    'sanitize_input',
    'normalize_email',
]

__version__ = '1.0.0'
