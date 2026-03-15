-- TechCorp Customer Success AI Agent - Database Setup
-- Create tables and insert sample data for tickets page

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TABLE 1: customers
-- ============================================================================
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Index for email lookups
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);

-- ============================================================================
-- TABLE 2: tickets
-- ============================================================================
CREATE TABLE IF NOT EXISTS tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID,
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    source_channel VARCHAR(50) NOT NULL,
    category VARCHAR(100),
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(50) DEFAULT 'open',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT
);

-- Indexes for ticket queries
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_channel ON tickets(source_channel);
CREATE INDEX IF NOT EXISTS idx_tickets_customer ON tickets(customer_id);
CREATE INDEX IF NOT EXISTS idx_tickets_priority ON tickets(priority);
CREATE INDEX IF NOT EXISTS idx_tickets_created ON tickets(created_at);
CREATE INDEX IF NOT EXISTS idx_tickets_category ON tickets(category);

-- ============================================================================
-- INSERT SAMPLE CUSTOMERS
-- ============================================================================
INSERT INTO customers (email, name, phone) VALUES
    ('sarah.johnson@acmecorp.com', 'Sarah Johnson', '+14155551234'),
    ('mike.chen@techstart.io', 'Mike Chen', '+14155552345'),
    ('david.park@innovate.com', 'David Park', '+14155553456'),
    ('emma.wilson@startup.co', 'Emma Wilson', '+14155554567'),
    ('robert.thompson@enterprise.com', 'Robert Thompson', '+14155555678'),
    ('jennifer.martinez@corp.com', 'Jennifer Martinez', '+14155556789'),
    ('alex.rivera@digital.io', 'Alex Rivera', '+14155557890'),
    ('lisa.anderson@cloud.com', 'Lisa Anderson', '+14155558901')
ON CONFLICT (email) DO NOTHING;

-- ============================================================================
-- INSERT SAMPLE TICKETS
-- ============================================================================
INSERT INTO tickets (customer_id, source_channel, category, priority, status, created_at) VALUES
    -- Recent tickets (last few hours)
    ((SELECT id FROM customers WHERE email = 'sarah.johnson@acmecorp.com'), 'email', 'billing', 'medium', 'open', NOW() - INTERVAL '15 minutes'),
    ((SELECT id FROM customers WHERE email = 'mike.chen@techstart.io'), 'whatsapp', 'technical', 'high', 'in_progress', NOW() - INTERVAL '32 minutes'),
    ((SELECT id FROM customers WHERE email = 'david.park@innovate.com'), 'web_form', 'technical', 'medium', 'open', NOW() - INTERVAL '1 hour'),
    ((SELECT id FROM customers WHERE email = 'emma.wilson@startup.co'), 'whatsapp', 'billing', 'low', 'resolved', NOW() - INTERVAL '3 hours'),
    ((SELECT id FROM customers WHERE email = 'robert.thompson@enterprise.com'), 'web_form', 'feedback', 'low', 'open', NOW() - INTERVAL '4 hours'),
    ((SELECT id FROM customers WHERE email = 'jennifer.martinez@corp.com'), 'email', 'technical', 'medium', 'in_progress', NOW() - INTERVAL '5 hours'),
    ((SELECT id FROM customers WHERE email = 'alex.rivera@digital.io'), 'whatsapp', 'bug_report', 'high', 'open', NOW() - INTERVAL '6 hours'),
    ((SELECT id FROM customers WHERE email = 'lisa.anderson@cloud.com'), 'email', 'general', 'medium', 'resolved', NOW() - INTERVAL '8 hours'),
    
    -- Older tickets (yesterday)
    ((SELECT id FROM customers WHERE email = 'sarah.johnson@acmecorp.com'), 'web_form', 'technical', 'high', 'in_progress', NOW() - INTERVAL '1 day'),
    ((SELECT id FROM customers WHERE email = 'mike.chen@techstart.io'), 'email', 'billing', 'critical', 'resolved', NOW() - INTERVAL '1 day'),
    
    -- Even older tickets
    ((SELECT id FROM customers WHERE email = 'david.park@innovate.com'), 'whatsapp', 'general', 'low', 'resolved', NOW() - INTERVAL '2 days'),
    ((SELECT id FROM customers WHERE email = 'emma.wilson@startup.co'), 'web_form', 'bug_report', 'medium', 'open', NOW() - INTERVAL '3 days'),
    ((SELECT id FROM customers WHERE email = 'robert.thompson@enterprise.com'), 'email', 'technical', 'high', 'in_progress', NOW() - INTERVAL '5 days'),
    ((SELECT id FROM customers WHERE email = 'jennifer.martinez@corp.com'), 'whatsapp', 'feedback', 'low', 'resolved', NOW() - INTERVAL '1 week');

-- ============================================================================
-- VERIFY DATA
-- ============================================================================
SELECT 'Customers created: ' || COUNT(*) FROM customers;
SELECT 'Tickets created: ' || COUNT(*) FROM tickets;

-- Show sample tickets with customer info
SELECT 
    t.id,
    t.source_channel as channel,
    t.category,
    t.priority,
    t.status,
    t.created_at,
    c.name as customer_name,
    c.email as customer_email
FROM tickets t
LEFT JOIN customers c ON t.customer_id = c.id
ORDER BY t.created_at DESC
LIMIT 5;
