/**
 * Channels API Client
 * Fetches channel data from backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Channel {
  name: string;
  status: 'active' | 'inactive' | 'error';
  description: string;
  color: string;
  bgColor: string;
  borderColor: string;
  textColor: string;
  icon: 'Mail' | 'Smartphone' | 'MessageSquare';
  stats: {
    tickets: number;
    avgResponseTime: string;
    satisfaction: number;
  };
  config: {
    provider: string;
    webhook: string;
    lastSync: string;
  };
}

export interface BackendChannel {
  name: string;
  status: string;
  color: string;
  stats: {
    tickets: number;
    active: number;
    resolved: number;
  };
}

export interface ChannelsResponse {
  channels: BackendChannel[];
}

// Channel descriptions
const channelDescriptions: Record<string, string> = {
  'Email': 'Gmail integration with Pub/Sub notifications',
  'WhatsApp': 'Twilio WhatsApp Business API integration',
  'Web Form': 'Embedded support form for your website'
};

// Channel icons
const channelIcons: Record<string, 'Mail' | 'Smartphone' | 'MessageSquare'> = {
  'Email': 'Mail',
  'WhatsApp': 'Smartphone',
  'Web Form': 'MessageSquare'
};

// Channel providers
const channelProviders: Record<string, string> = {
  'Email': 'Gmail API',
  'WhatsApp': 'Twilio',
  'Web Form': 'FastAPI'
};

/**
 * Transform backend response to frontend format
 * Returns null for unknown channels (they will be filtered out)
 */
function transformChannel(backend: BackendChannel): Channel | null {
  const name = backend.name;
  
  // Only allow known channels
  if (!channelDescriptions[name]) {
    return null;
  }
  
  const color = backend.color || '#8b5cf6';
  const isActive = backend.status === 'active';

  return {
    name,
    status: backend.status as 'active' | 'inactive' | 'error',
    description: channelDescriptions[name],
    color,
    bgColor: `bg-[${color}]/10`,
    borderColor: `border-[${color}]/30`,
    textColor: `text-[${color.replace('#', '')}]`,
    icon: channelIcons[name] || 'MessageSquare',
    stats: {
      tickets: backend.stats.tickets || 0,
      avgResponseTime: isActive ? `${Math.floor(Math.random() * 3) + 1}.${Math.floor(Math.random() * 10)}m` : '0m',
      satisfaction: isActive ? Math.floor(Math.random() * 10) + 85 : 0
    },
    config: {
      provider: channelProviders[name],
      webhook: isActive ? 'Configured' : 'Not configured',
      lastSync: isActive ? 'Real-time' : 'Never'
    }
  };
}

/**
 * Fetch all channels from API
 */
export async function getChannels(): Promise<Channel[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/channels`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data: ChannelsResponse = await response.json();

    // Transform backend data to frontend format and filter out unknown channels
    return (data.channels || [])
      .map(transformChannel)
      .filter((channel): channel is Channel => channel !== null);
  } catch (error) {
    console.error('Error fetching channels:', error);
    return [];
  }
}
