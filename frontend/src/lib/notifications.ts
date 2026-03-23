/**
 * TechCorp Customer Success AI Agent - Notifications Client Library
 * Handles all notification-related API calls
 */

// Get the API base URL from environment or use default
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://fahadmemon1234-ai-powered-customer-success-fte.hf.space';

export interface Notification {
  id: string;
  type: string;
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  icon: string;
  color: string;
  url: string;
  data: {
    reference_id?: string;
    reference_type?: string;
    [key: string]: any;
  };
}

export interface NotificationsResponse {
  notifications: Notification[];
  total: number;
  unread: number;
  has_more: boolean;
}

export interface UnreadCountResponse {
  unread: number;
}

export interface MarkReadResponse {
  success: boolean;
  message: string;
  notification_id?: string;
  updated_count?: number;
}

/**
 * Fetch notifications from the API
 * @param limit - Maximum number of notifications to return (default: 20)
 * @param unreadOnly - Whether to return only unread notifications (default: false)
 * @returns Promise with notifications response
 */
export async function getNotifications(
  limit: number = 20,
  unreadOnly: boolean = false
): Promise<NotificationsResponse> {
  try {
    const url = `${API_BASE_URL}/api/notifications?limit=${limit}&unread_only=${unreadOnly}`;
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Get notifications error:', error);
    throw error;
  }
}

/**
 * Get count of unread notifications
 * @returns Promise with unread count
 */
export async function getUnreadCount(): Promise<UnreadCountResponse> {
  try {
    const url = `${API_BASE_URL}/api/notifications/unread-count`;
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Get unread count error:', error);
    return { unread: 0 }; // Return 0 on error to avoid breaking the UI
  }
}

/**
 * Mark a single notification as read
 * @param notificationId - ID of the notification to mark as read
 * @returns Promise with mark read response
 */
export async function markSingleAsRead(notificationId: string): Promise<MarkReadResponse> {
  try {
    const url = `${API_BASE_URL}/api/notifications/mark-read?notification_id=${notificationId}`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Mark notification as read error:', error);
    throw error;
  }
}

/**
 * Mark all notifications as read
 * @returns Promise with mark all read response
 */
export async function markAllAsRead(): Promise<MarkReadResponse> {
  try {
    const url = `${API_BASE_URL}/api/notifications/mark-all-read`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Mark all as read error:', error);
    throw error;
  }
}

/**
 * Alias for markAllAsRead for backwards compatibility
 */
export const markAsRead = markAllAsRead;

/**
 * Get notification statistics
 * @returns Promise with notification stats
 */
export async function getNotificationStats(): Promise<{
  today: number;
  this_week: number;
  this_month: number;
}> {
  try {
    const url = `${API_BASE_URL}/api/notifications/stats`;
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Get notification stats error:', error);
    return {
      today: 0,
      this_week: 0,
      this_month: 0,
    };
  }
}
