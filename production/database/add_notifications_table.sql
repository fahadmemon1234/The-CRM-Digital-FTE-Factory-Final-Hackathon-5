-- Apply notifications table to existing database
-- Run this on your database to add the notifications table

-- Enable uuid extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TABLE: notifications
-- ============================================================================
-- Purpose: Store user notifications for read/unread tracking
-- Tracks notifications for new tickets, updates, messages, etc.
-- Supports "Mark as All Read" functionality

CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255),  -- Can be null for system-wide notifications
    notification_type VARCHAR(50) NOT NULL,  -- 'NEW_TICKET', 'TICKET_UPDATED', 'NEW_MESSAGE', 'URGENT_TICKET'
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    url VARCHAR(500),  -- Link to related resource
    is_read BOOLEAN DEFAULT FALSE,  -- Read status: 0 = unread, 1 = read
    reference_id VARCHAR(100),  -- Reference to related entity (ticket_id, message_id, etc.)
    reference_type VARCHAR(50),  -- Type of reference ('ticket', 'message', 'conversation')
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'
);

-- Indexes for efficient queries
DROP INDEX IF EXISTS idx_notifications_user_id;
CREATE INDEX idx_notifications_user_id ON notifications(user_id);

DROP INDEX IF EXISTS idx_notifications_is_read;
CREATE INDEX idx_notifications_is_read ON notifications(is_read);

DROP INDEX IF EXISTS idx_notifications_created_at;
CREATE INDEX idx_notifications_created_at ON notifications(created_at);

DROP INDEX IF EXISTS idx_notifications_type;
CREATE INDEX idx_notifications_type ON notifications(notification_type);

DROP INDEX IF EXISTS idx_notifications_reference;
CREATE INDEX idx_notifications_reference ON notifications(reference_type, reference_id);

-- Composite index for common query pattern (unread notifications for user)
DROP INDEX IF EXISTS idx_notifications_user_unread;
CREATE INDEX idx_notifications_user_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;

COMMENT ON TABLE notifications IS 'User notifications with read/unread tracking';
COMMENT ON COLUMN notifications.is_read IS 'False = unread, True = read';
COMMENT ON COLUMN notifications.read_at IS 'Timestamp when notification was marked as read';
COMMENT ON COLUMN notifications.reference_id IS 'ID of related entity (ticket_id, message_id, etc.)';
COMMENT ON COLUMN notifications.reference_type IS 'Type of related entity: ticket, message, conversation';

-- Sample test data (optional - for testing)
-- INSERT INTO notifications (notification_type, title, message, url, reference_id, reference_type, metadata)
-- VALUES 
--     ('NEW_TICKET', 'New Ticket', 'A new ticket has been created', '/dashboard/tickets/1', '1', 'ticket', '{"icon": "ticket", "color": "blue"}'),
--     ('URGENT_TICKET', 'Urgent Ticket', 'Urgent ticket requires attention', '/dashboard/tickets/2', '2', 'ticket', '{"icon": "alert", "color": "red"}'),
--     ('NEW_MESSAGE', 'New Message', 'Customer sent a new message', '/dashboard/tickets/1', '1', 'message', '{"icon": "message", "color": "green"}');
