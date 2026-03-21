// WhatsApp API Service
const API_BASE_URL = 'http://localhost:8000';

export interface WhatsAppMessage {
  from: string;
  body: string;
  to?: string;
  MessageSid?: string;
}

export interface WhatsAppResponse {
  status: string;
  ticket_id?: string;
  message_sid?: string;
  error?: string;
}

/**
 * Send WhatsApp message via Twilio
 * Note: This requires Twilio sandbox setup
 */
export async function sendWhatsAppMessage(phone: string, message: string): Promise<WhatsAppResponse> {
  try {
    // For testing, we'll use the webhook endpoint
    // In production, Twilio handles inbound messages via webhook
    const response = await fetch(`${API_BASE_URL}/webhooks/whatsapp`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        From: `whatsapp:${phone}`,
        Body: message,
        To: 'whatsapp:+14155238886', // Twilio sandbox number
        MessageSid: `SM${Date.now()}` // Mock SID
      })
    });

    if (!response.ok) {
      throw new Error('Failed to send WhatsApp message');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error sending WhatsApp message:', error);
    return {
      status: 'error',
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}

/**
 * Simulate receiving WhatsApp message (for testing)
 */
export async function simulateWhatsAppMessage(phone: string, message: string): Promise<WhatsAppResponse> {
  console.log('📱 Simulating WhatsApp message:', { phone, message });
  
  // Add whatsapp: prefix if not present
  const formattedPhone = phone.startsWith('whatsapp:') ? phone : `whatsapp:${phone}`;
  
  const response = await fetch(`${API_BASE_URL}/webhooks/whatsapp`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
      From: formattedPhone,
      Body: message,
      To: 'whatsapp:+14155238886',
      MessageSid: `SM${Math.random().toString(36).substring(7)}`
    })
  });

  const data = await response.json();
  console.log('📨 WhatsApp response:', data);
  
  return data;
}

/**
 * Get WhatsApp status
 */
export async function getWhatsAppStatus(): Promise<{ connected: boolean; number?: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    const health = await response.json();
    
    return {
      connected: health.channels?.whatsapp === 'active',
      number: process.env.NEXT_PUBLIC_TWILIO_WHATSAPP_NUMBER
    };
  } catch (error) {
    console.error('Error checking WhatsApp status:', error);
    return { connected: false };
  }
}
