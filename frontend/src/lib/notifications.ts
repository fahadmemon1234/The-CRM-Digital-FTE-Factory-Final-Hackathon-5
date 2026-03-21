/**
 * Notifications API Client
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Notification {
  id: string;
  type: string;
  title: string;
  message: string;
  timestamp: string | null;
  read: boolean;
  icon: string;
  color: string;
  url: string;
  data: any;
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

export interface NotificationStats {
  today: number;
  this_week: number;
  this_month: number;
}

/**
 * Get notifications
 */
export async function getNotifications(
  limit: number = 20,
  unreadOnly: boolean = false
): Promise<NotificationsResponse> {
  try {
    const url = new URL(`${API_BASE_URL}/api/notifications`);
    url.searchParams.set('limit', limit.toString());
    if (unreadOnly) {
      url.searchParams.set('unread_only', 'true');
    }

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Get notifications error:', error);
    return { notifications: [], total: 0, unread: 0, has_more: false };
  }
}

/**
 * Get unread count
 */
export async function getUnreadCount(): Promise<UnreadCountResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/notifications/unread-count`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Get unread count error:', error);
    return { unread: 0 };
  }
}

/**
 * Mark notification as read
 */
export async function markAsRead(notificationId: string): Promise<any> {
  try {
    const url = new URL(`${API_BASE_URL}/api/notifications/mark-read`);
    url.searchParams.set('notification_id', notificationId);

    const response = await fetch(url.toString(), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Mark as read error:', error);
    return null;
  }
}

/**
 * Mark all notifications as read
 */
export async function markAllAsRead(): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/notifications/mark-all-read`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json()
  } catch (error) {
    console.error('Mark all as read error:', error)
    return null
  }
}

/**
 * Mark single notification as read
 */
export async function markSingleAsRead(notificationId: string): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/notifications/mark-read`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ notification_id: notificationId })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json()
  } catch (error) {
    console.error('Mark as read error:', error)
    return null
  }
}

/**
 * Get notification stats
 */
export async function getNotificationStats(): Promise<NotificationStats> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/notifications/stats`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Get stats error:', error);
    return { today: 0, this_week: 0, this_month: 0 };
  }
}

/**
 * Get icon for notification type
 */
export function getNotificationIcon(type: string): string {
  switch (type) {
    case 'NEW_TICKET':
      return 'ticket';
    case 'TICKET_UPDATED':
      return 'refresh';
    case 'NEW_MESSAGE':
      return 'message';
    case 'URGENT_TICKET':
      return 'alert';
    case 'CUSTOMER_FOLLOWUP':
      return 'user';
    default:
      return 'bell';
  }
}

/**
 * Get color for notification type
 */
export function getNotificationColor(type: string): string {
  switch (type) {
    case 'URGENT_TICKET':
      return 'red';
    case 'NEW_TICKET':
      return 'blue';
    case 'TICKET_UPDATED':
      return 'purple';
    case 'NEW_MESSAGE':
      return 'green';
    case 'CUSTOMER_FOLLOWUP':
      return 'orange';
    default:
      return 'neutral';
  }
}
