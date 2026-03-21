/**
 * API Client for TechCorp FTE Backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Ticket {
  id: string;
  channel: string;
  category: string;
  priority: string;
  status: string;
  time: string;
  customer_name: string | null;
  customer_email: string | null;
}

export interface DashboardStats {
  totalTickets: number;
  resolvedTickets: number;
  pendingTickets: number;
  avgResponseTime: string;
}

export interface ChannelStats {
  name: string;
  count: number;
  percentage: number;
}

export interface CategoryStats {
  name: string;
  value: number;
}

/**
 * Fetch tickets from API
 */
export async function fetchTickets(limit: number = 100, offset: number = 0): Promise<Ticket[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/tickets?limit=${limit}&offset=${offset}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data.tickets || [];
  } catch (error) {
    console.error('Error fetching tickets:', error);
    return [];
  }
}

/**
 * Fetch dashboard statistics
 */
export async function fetchDashboardStats(): Promise<DashboardStats> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/tickets/stats`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    console.log('Dashboard stats response:', data);

    return {
      totalTickets: data.total || 0,
      resolvedTickets: data.resolved || 0,
      pendingTickets: data.pending || 0,
      avgResponseTime: data.avg_response || data.avgResponseTime || data.avg_response_time || '2.4m'
    };
  } catch (error) {
    console.error('Error fetching stats:', error);
    return {
      totalTickets: 0,
      resolvedTickets: 0,
      pendingTickets: 0,
      avgResponseTime: '0m'
    };
  }
}

/**
 * Fetch channel statistics
 */
export async function fetchChannelStats(): Promise<ChannelStats[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/tickets/channels`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    console.log('Channel stats response:', data);
    return data.channels || [];
  } catch (error) {
    console.error('Error fetching channel stats:', error);
    return [];
  }
}

/**
 * Fetch category statistics
 */
export async function fetchCategoryStats(): Promise<CategoryStats[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/tickets/categories`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    console.log('Category stats response:', data);
    return data.categories || [];
  } catch (error) {
    console.error('Error fetching category stats:', error);
    return [];
  }
}

/**
 * Get relative time string
 */
export function getRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) {
    return 'Just now';
  } else if (diffInSeconds < 3600) {
    return `${Math.floor(diffInSeconds / 60)}m ago`;
  } else if (diffInSeconds < 86400) {
    return `${Math.floor(diffInSeconds / 3600)}h ago`;
  } else {
    return `${Math.floor(diffInSeconds / 86400)}d ago`;
  }
}

/**
 * Fetch ticket activity data for charts
 */
export interface ActivityData {
  time: string;
  tickets: number;
  resolved: number;
}

export async function fetchActivityData(): Promise<ActivityData[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/tickets/activity`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data.activity || [];
  } catch (error) {
    console.error('Error fetching activity data:', error);
    return [];
  }
}
