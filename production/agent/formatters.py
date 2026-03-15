"""
TechCorp Customer Success AI Agent - Response Formatters

This module provides channel-specific response formatting functions.
"""

from typing import Optional


def format_for_channel(response: str, channel: str, 
                       customer_name: Optional[str] = None,
                       ticket_id: Optional[str] = None) -> str:
    """
    Format a response message for the specified communication channel.
    
    Args:
        response: The raw response content to format
        channel: One of "email", "whatsapp", or "web_form"
        customer_name: Optional customer name for personalization
        ticket_id: Optional ticket reference number
        
    Returns:
        Formatted response string appropriate for the channel
    """
    if channel == "email":
        return _format_email(response, customer_name, ticket_id)
    elif channel == "whatsapp":
        return _format_whatsapp(response)
    elif channel == "web_form":
        return _format_web_form(response, ticket_id)
    else:
        # Default to web_form style for unknown channels
        return response


def _format_email(response: str, customer_name: Optional[str] = None,
                  ticket_id: Optional[str] = None) -> str:
    """
    Format response for email channel.
    
    - Formal, detailed style
    - Required greeting: "Dear [Name]," or "Dear Customer,"
    - Required signature with ticket reference
    - Up to 500 words acceptable
    """
    # Determine greeting
    if customer_name:
        greeting = f"Dear {customer_name},"
    else:
        greeting = "Dear Customer,"
    
    # Build signature with ticket reference
    signature = "Best regards,\nTechCorp AI Support Team\nsupport@techcorp.com"
    if ticket_id:
        signature += f"\n\nTicket Reference: {ticket_id}"
    
    # Assemble email
    email = f"""{greeting}

Thank you for reaching out to TechCorp Support.

{response}

If you have any other questions, please don't hesitate to reach out.

{signature}"""
    
    return email


def _format_whatsapp(response: str) -> str:
    """
    Format response for WhatsApp channel.
    
    - Casual, concise style
    - Trim to 300 characters maximum
    - Add required footer with emoji
    - Optional greeting emoji (1 max)
    """
    # Required footer for WhatsApp
    footer = "📱 Reply for more help or type 'human' for live support."
    
    # Calculate max response length (300 chars - footer - spacing)
    max_response_length = 300 - len(footer) - 2  # 2 for newlines
    
    # Trim response if needed
    if len(response) > max_response_length:
        response = response[:max_response_length - 3] + "..."
    
    # Assemble WhatsApp message
    whatsapp_message = f"{response}\n\n{footer}"
    
    return whatsapp_message


def _format_web_form(response: str, ticket_id: Optional[str] = None) -> str:
    """
    Format response for web form channel.
    
    - Semi-formal, balanced detail
    - Required greeting: "Hello,"
    - Required footer with support portal link
    - Optional ticket reference
    - Up to 300 words acceptable
    """
    # Required footer for web form
    footer = "---\nNeed more help? Reply to this message or visit our support portal."
    if ticket_id:
        footer += f"\n\nTicket Reference: {ticket_id}"
    
    # Assemble web form response
    web_form = f"""Hello,

Thanks for contacting TechCorp Support.

{response}

{footer}

Best,
TechCorp Support"""
    
    return web_form


def get_channel_limits(channel: str) -> dict:
    """
    Get the formatting limits and requirements for a channel.
    
    Args:
        channel: One of "email", "whatsapp", or "web_form"
        
    Returns:
        Dictionary with channel formatting requirements
    """
    limits = {
        "email": {
            "max_words": 500,
            "max_chars": 3000,
            "greeting_required": True,
            "signature_required": True,
            "footer_required": False,
            "emoji_allowed": False,
            "style": "formal"
        },
        "whatsapp": {
            "max_words": None,
            "max_chars": 300,
            "greeting_required": False,
            "signature_required": False,
            "footer_required": True,
            "emoji_allowed": True,
            "max_emoji": 2,
            "style": "casual"
        },
        "web_form": {
            "max_words": 300,
            "max_chars": 2000,
            "greeting_required": True,
            "signature_required": True,
            "footer_required": True,
            "emoji_allowed": False,
            "style": "semi-formal"
        }
    }
    
    return limits.get(channel, limits["web_form"])


def validate_response_length(response: str, channel: str) -> tuple[bool, str]:
    """
    Validate that a response meets channel length requirements.
    
    Args:
        response: The formatted response to validate
        channel: One of "email", "whatsapp", or "web_form"
        
    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    limits = get_channel_limits(channel)
    
    # Check character limit
    if limits.get("max_chars"):
        if len(response) > limits["max_chars"]:
            return (False, f"Response exceeds {limits['max_chars']} character limit for {channel}")
    
    # Check word limit
    if limits.get("max_words"):
        word_count = len(response.split())
        if word_count > limits["max_words"]:
            return (False, f"Response exceeds {limits['max_words']} word limit for {channel}")
    
    return (True, "Response meets length requirements")


def trim_to_channel_limit(response: str, channel: str) -> str:
    """
    Trim a response to fit within channel limits.
    
    Args:
        response: The response to trim
        channel: One of "email", "whatsapp", or "web_form"
        
    Returns:
        Trimmed response string
    """
    limits = get_channel_limits(channel)
    
    # WhatsApp has strict character limit
    if channel == "whatsapp" and limits.get("max_chars"):
        if len(response) > limits["max_chars"]:
            return response[:limits["max_chars"] - 3] + "..."
    
    # For email and web form, trim by words if needed
    if limits.get("max_words"):
        words = response.split()
        if len(words) > limits["max_words"]:
            trimmed = " ".join(words[:limits["max_words"]])
            return trimmed + "..."
    
    return response


def add_ticket_reference(response: str, ticket_id: str, channel: str) -> str:
    """
    Add a ticket reference to an existing response.
    
    Args:
        response: The existing response
        ticket_id: The ticket ID to add
        channel: One of "email", "whatsapp", or "web_form"
        
    Returns:
        Response with ticket reference added
    """
    if channel == "email":
        # Add to signature area
        if ticket_id not in response:
            response += f"\n\nTicket Reference: {ticket_id}"
    elif channel == "web_form":
        # Add to footer area
        if ticket_id not in response:
            response += f"\n\nTicket: {ticket_id}"
    # WhatsApp doesn't include ticket IDs (character limit)
    
    return response
