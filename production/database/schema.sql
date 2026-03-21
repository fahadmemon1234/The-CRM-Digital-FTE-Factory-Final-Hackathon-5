-- ============================================================================
-- TechCorp Customer Success AI Agent - CRM Database Schema
-- ============================================================================
-- 
-- This is the complete CRM/Ticket Management system for TechCorp.
-- It replaces Salesforce/HubSpot for this project.
--
-- Database: PostgreSQL 15+ with pgvector extension
-- Purpose: Store customer data, conversations, messages, tickets, and analytics
--
-- INCUBATION MAPPING:
-- -------------------
-- Incubation: In-memory Python dicts (conversations, tickets, messages)
-- Production: PostgreSQL with normalized schema and vector search
--
-- Key Changes from Incubation:
-- - conversations dict → conversations table with full audit trail
-- - tickets dict → tickets table with SLA tracking
-- - messages list → messages table with delivery tracking
-- - customer_history dict → customers + customer_identifiers tables
-- - In-memory search → pgvector semantic search
--
-- Author: AI Engineering Team
-- Version: 1.0.0 (Production CRM)
-- Based on: In-memory storage (Incubation)
-- ============================================================================

-- Enable required extensions
-- INCUBATION: No extensions (pure Python)
-- PRODUCTION: PostgreSQL extensions for UUID and vector search
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";

-- ============================================================================
-- TABLE 1: customers
-- ============================================================================
-- INCUBATION: customer_id as dict key in prototype.py
-- PRODUCTION: Normalized customers table with JSONB metadata
--
-- Purpose: Core customer identity table
-- Primary Key: UUID (random, not sequential for security)
-- Unique Constraint: email (customers identified by email across channels)

CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Index for email lookups (most common query pattern)
CREATE INDEX idx_customers_email ON customers(email);

-- Comment for documentation
COMMENT ON TABLE customers IS 'Core customer identity table - customers are identified by email across all channels';
COMMENT ON COLUMN customers.metadata IS 'Flexible JSONB field for custom attributes (tier, company, preferences, etc.)';

-- ============================================================================
-- TABLE 2: customer_identifiers
-- ============================================================================
-- INCUBATION: Cross-channel identity via email in prototype.py
-- PRODUCTION: Dedicated table for multiple identifiers per customer
--
-- Purpose: Support cross-channel identity resolution
-- A customer may have multiple emails, phones, WhatsApp numbers
-- All identifiers link back to single customer record

CREATE TABLE customer_identifiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    identifier_type VARCHAR(50) NOT NULL,  -- 'email', 'phone', 'whatsapp', 'web_form_id'
    identifier_value VARCHAR(255) NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure no duplicate identifiers
    UNIQUE(identifier_type, identifier_value)
);

-- Index for identifier lookups (cross-channel identity resolution)
CREATE INDEX idx_customer_identifiers_value ON customer_identifiers(identifier_value);
CREATE INDEX idx_customer_identifiers_customer ON customer_identifiers(customer_id);

COMMENT ON TABLE customer_identifiers IS 'Cross-channel identity resolution - links multiple identifiers to single customer';
COMMENT ON COLUMN customer_identifiers.identifier_type IS 'Type of identifier: email, phone, whatsapp, web_form_id';
COMMENT ON COLUMN customer_identifiers.verified IS 'True if identifier has been verified (email confirmed, phone verified, etc.)';

-- ============================================================================
-- TABLE 3: conversations
-- ============================================================================
-- INCUBATION: ConversationState dataclass in prototype.py
-- PRODUCTION: Full conversation tracking with sentiment and escalation
--
-- Purpose: Track conversation sessions across channels
-- A conversation may span multiple channels (WhatsApp → Email follow-up)
-- Tracks sentiment, resolution, and escalation info

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    initial_channel VARCHAR(50) NOT NULL,  -- 'email', 'whatsapp', 'web_form'
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'active',  -- 'active', 'resolved', 'escalated', 'closed'
    sentiment_score DECIMAL(3,2),  -- 0.00 to 1.00
    resolution_type VARCHAR(50),  -- 'resolved_by_ai', 'escalated_to_human', 'customer_abandoned'
    escalated_to VARCHAR(255),  -- Team name if escalated (Sales, Billing, Legal, etc.)
    metadata JSONB DEFAULT '{}'
);

-- Indexes for common query patterns
CREATE INDEX idx_conversations_customer ON conversations(customer_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_channel ON conversations(initial_channel);
CREATE INDEX idx_conversations_started ON conversations(started_at);

COMMENT ON TABLE conversations IS 'Conversation sessions - tracks customer interactions across channels';
COMMENT ON COLUMN conversations.initial_channel IS 'Channel where conversation started (for analytics)';
COMMENT ON COLUMN conversations.sentiment_score IS 'Average sentiment score across conversation (0.00-1.00)';
COMMENT ON COLUMN conversations.escalated_to IS 'Team name if escalated: Sales Team, Billing Team, Legal Team, Security Team, Senior Support';

-- ============================================================================
-- TABLE 4: messages
-- ============================================================================
-- INCUBATION: Message dataclass list in ConversationState
-- PRODUCTION: Full message audit trail with delivery tracking
--
-- Purpose: Store every message in every conversation
-- Tracks both inbound (customer) and outbound (agent) messages
-- Includes latency, tokens, tool calls for AI analytics

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    channel VARCHAR(50) NOT NULL,  -- 'email', 'whatsapp', 'web_form'
    direction VARCHAR(20) NOT NULL,  -- 'inbound', 'outbound'
    role VARCHAR(20) NOT NULL,  -- 'customer', 'agent', 'system'
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tokens_used INTEGER,  -- For AI cost tracking
    latency_ms INTEGER,  -- Response latency for performance monitoring
    tool_calls JSONB DEFAULT '[]',  -- Tools invoked (search_knowledge_base, create_ticket, etc.)
    channel_message_id VARCHAR(255),  -- External ID (Gmail message ID, WhatsApp message ID)
    delivery_status VARCHAR(50) DEFAULT 'pending'  -- 'pending', 'sent', 'delivered', 'failed'
);

-- Indexes for message queries
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_channel ON messages(channel);
CREATE INDEX idx_messages_direction ON messages(direction);
CREATE INDEX idx_messages_created ON messages(created_at);
CREATE INDEX idx_messages_delivery ON messages(delivery_status);

COMMENT ON TABLE messages IS 'Complete message audit trail - every message in every conversation';
COMMENT ON COLUMN messages.tool_calls IS 'JSON array of tools invoked: [{"tool": "search_knowledge_base", "latency_ms": 45}, ...]';
COMMENT ON COLUMN messages.channel_message_id IS 'External channel message ID for delivery confirmation';

-- ============================================================================
-- TABLE 5: tickets
-- ============================================================================
-- INCUBATION: tickets dict in mcp_server.py
-- PRODUCTION: Full ticket management with SLA tracking
--
-- Purpose: Track support tickets for issue resolution
-- Tickets are created for each customer issue
-- Linked to conversations for full context

CREATE TABLE tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    source_channel VARCHAR(50) NOT NULL,  -- Channel where ticket originated
    category VARCHAR(100),  -- 'billing', 'technical', 'general', 'bug_report', 'feedback'
    priority VARCHAR(20) DEFAULT 'medium',  -- 'low', 'medium', 'high', 'critical'
    status VARCHAR(50) DEFAULT 'open',  -- 'open', 'in_progress', 'pending', 'resolved', 'closed', 'escalated'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT
);

-- Indexes for ticket queries
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_channel ON tickets(source_channel);
CREATE INDEX idx_tickets_customer ON tickets(customer_id);
CREATE INDEX idx_tickets_priority ON tickets(priority);
CREATE INDEX idx_tickets_created ON tickets(created_at);
CREATE INDEX idx_tickets_category ON tickets(category);

COMMENT ON TABLE tickets IS 'Support ticket tracking - issues created for customer problems';
COMMENT ON COLUMN tickets.category IS 'Issue category: billing, technical, general, bug_report, feedback';
COMMENT ON COLUMN tickets.priority IS 'Priority level: low, medium, high, critical';

-- ============================================================================
-- TABLE 6: knowledge_base
-- ============================================================================
-- INCUBATION: product-docs.md file with keyword search
-- PRODUCTION: pgvector semantic search with embeddings
--
-- Purpose: Store documentation for AI agent retrieval
-- Vector embeddings enable semantic search (not just keyword)
-- "reset password" matches "forgot password" via similarity

CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),  -- 'account', 'billing', 'technical', 'integrations', 'api'
    embedding VECTOR(1536),  -- OpenAI text-embedding-ada-002 dimension
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Vector index for semantic search (IVFFlat for efficient similarity search)
-- INCUBATION: No vector search (keyword only)
-- PRODUCTION: pgvector cosine similarity search
CREATE INDEX idx_knowledge_embedding ON knowledge_base 
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Regular index for category filtering
CREATE INDEX idx_knowledge_category ON knowledge_base(category);

COMMENT ON TABLE knowledge_base IS 'AI agent knowledge base with vector embeddings for semantic search';
COMMENT ON COLUMN knowledge_base.embedding IS '1536-dimension embedding from OpenAI text-embedding-ada-002';

-- ============================================================================
-- TABLE 7: channel_configs
-- ============================================================================
-- INCUBATION: Hardcoded channel formatting in prototype.py
-- PRODUCTION: Database-driven channel configuration
--
-- Purpose: Store channel-specific configuration
-- Enables runtime configuration changes without code deployment
-- Stores response templates, length limits, API credentials

CREATE TABLE channel_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    channel VARCHAR(50) UNIQUE NOT NULL,  -- 'email', 'whatsapp', 'web_form'
    enabled BOOLEAN DEFAULT TRUE,
    config JSONB NOT NULL,  -- Channel-specific config (API endpoints, credentials, etc.)
    response_template TEXT,  -- Template for responses (greeting, signature, footer)
    max_response_length INTEGER,  -- Character limit for channel
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for channel lookups
CREATE INDEX idx_channel_configs_channel ON channel_configs(channel);

COMMENT ON TABLE channel_configs IS 'Channel-specific configuration - enables runtime config changes';
COMMENT ON COLUMN channel_configs.config IS 'JSONB with channel-specific settings (API keys, endpoints, etc.)';

-- Insert default channel configurations
INSERT INTO channel_configs (channel, enabled, config, response_template, max_response_length) VALUES
    ('email', TRUE, 
     '{"smtp_host": "smtp.techcorp.com", "smtp_port": 587, "from_address": "support@techcorp.com"}'::jsonb,
     'Dear {{customer_name}},\n\nThank you for reaching out to TechCorp Support.\n\n{{response}}\n\nIf you have any other questions, please don''t hesitate to reach out.\n\nBest regards,\nTechCorp AI Support Team\nsupport@techcorp.com',
     3000),
    ('whatsapp', TRUE,
     '{"api_provider": "twilio", "phone_number": "+1234567890"}'::jsonb,
     '{{response}}\n\n📱 Reply for more help or type ''human'' for live support.',
     300),
    ('web_form', TRUE,
     '{"form_endpoint": "/api/web-form", "notification_email": "support@techcorp.com"}'::jsonb,
     'Hello,\n\nThanks for contacting TechCorp Support.\n\n{{response}}\n\n---\nNeed more help? Reply to this message or visit our support portal.\n\nBest,\nTechCorp Support',
     2000)
ON CONFLICT (channel) DO NOTHING;

-- ============================================================================
-- TABLE 8: agent_metrics
-- ============================================================================
-- INCUBATION: No metrics tracking (print statements only)
-- PRODUCTION: Comprehensive metrics for monitoring and analytics
--
-- Purpose: Track AI agent performance metrics
-- Response times, accuracy, escalation rates, sentiment trends
-- Enables data-driven optimization

CREATE TABLE agent_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(100) NOT NULL,  -- 'response_time_ms', 'escalation_rate', 'resolution_rate', 'avg_sentiment'
    metric_value DECIMAL(10,4) NOT NULL,
    channel VARCHAR(50),  -- Optional channel breakdown
    dimensions JSONB DEFAULT '{}',  -- Additional dimensions (hour, day, model_version, etc.)
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for metric queries
CREATE INDEX idx_agent_metrics_name ON agent_metrics(metric_name);
CREATE INDEX idx_agent_metrics_channel ON agent_metrics(channel);
CREATE INDEX idx_agent_metrics_recorded ON agent_metrics(recorded_at);
CREATE INDEX idx_agent_metrics_dimensions ON agent_metrics USING GIN (dimensions);

COMMENT ON TABLE agent_metrics IS 'AI agent performance metrics - response times, accuracy, escalation rates, sentiment';
COMMENT ON COLUMN agent_metrics.dimensions IS 'JSONB with additional dimensions for slicing metrics';

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Auto-update updated_at timestamp for knowledge_base
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_knowledge_base_updated_at
    BEFORE UPDATE ON knowledge_base
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Auto-set ended_at when conversation status changes to resolved/closed
CREATE OR REPLACE FUNCTION set_conversation_ended_at()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status IN ('resolved', 'closed') AND OLD.status NOT IN ('resolved', 'closed') THEN
        NEW.ended_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_conversation_ended_at_trigger
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION set_conversation_ended_at();

-- Auto-set resolved_at when ticket status changes to resolved
CREATE OR REPLACE FUNCTION set_ticket_resolved_at()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'resolved' AND OLD.status != 'resolved' THEN
        NEW.resolved_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_ticket_resolved_at_trigger
    BEFORE UPDATE ON tickets
    FOR EACH ROW
    EXECUTE FUNCTION set_ticket_resolved_at();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Active conversations with customer info
CREATE VIEW active_conversations AS
SELECT 
    c.id as conversation_id,
    c.customer_id,
    cu.email as customer_email,
    cu.name as customer_name,
    c.initial_channel,
    c.started_at,
    c.status,
    c.sentiment_score,
    c.escalated_to,
    COUNT(m.id) as message_count
FROM conversations c
JOIN customers cu ON c.customer_id = cu.id
LEFT JOIN messages m ON c.id = m.conversation_id
WHERE c.status = 'active'
GROUP BY c.id, cu.email, cu.name;

-- Open tickets with SLA status
CREATE VIEW open_tickets_with_sla AS
SELECT 
    t.id as ticket_id,
    t.customer_id,
    cu.email as customer_email,
    t.source_channel,
    t.category,
    t.priority,
    t.status,
    t.created_at,
    CASE 
        WHEN t.created_at + INTERVAL '24 hours' < NOW() AND t.priority = 'medium' THEN 'breached'
        WHEN t.created_at + INTERVAL '4 hours' < NOW() AND t.priority = 'high' THEN 'breached'
        WHEN t.created_at + INTERVAL '1 hour' < NOW() AND t.priority = 'critical' THEN 'breached'
        ELSE 'on_track'
    END as sla_status
FROM tickets t
JOIN customers cu ON t.customer_id = cu.id
WHERE t.status IN ('open', 'in_progress', 'pending');

-- Channel performance metrics (last 24 hours)
CREATE VIEW channel_performance_24h AS
SELECT 
    m.channel,
    COUNT(*) as total_messages,
    COUNT(*) FILTER (WHERE m.direction = 'inbound') as inbound_messages,
    COUNT(*) FILTER (WHERE m.direction = 'outbound') as outbound_messages,
    AVG(m.latency_ms) as avg_latency_ms,
    SUM(m.tokens_used) as total_tokens,
    COUNT(*) FILTER (WHERE m.delivery_status = 'delivered') * 100.0 / NULLIF(COUNT(*), 0) as delivery_rate
FROM messages m
WHERE m.created_at > NOW() - INTERVAL '24 hours'
GROUP BY m.channel;

-- Customer conversation summary
CREATE VIEW customer_summary AS
SELECT 
    cu.id as customer_id,
    cu.email,
    cu.name,
    COUNT(DISTINCT c.id) as total_conversations,
    COUNT(DISTINCT t.id) as total_tickets,
    COUNT(DISTINCT t.id) FILTER (WHERE t.status = 'escalated') as escalated_tickets,
    AVG(c.sentiment_score) as avg_sentiment,
    MAX(c.started_at) as last_contact,
    cu.created_at as customer_since
FROM customers cu
LEFT JOIN conversations c ON cu.id = c.customer_id
LEFT JOIN tickets t ON cu.id = t.customer_id
GROUP BY cu.id;

-- ============================================================================
-- SEED DATA (Development/Testing)
-- ============================================================================

-- Sample customers for testing
INSERT INTO customers (email, name, phone, metadata) VALUES
    ('john.doe@example.com', 'John Doe', '+1-555-0101', '{"tier": "growth", "company": "Acme Corp"}'::jsonb),
    ('sarah.johnson@acmecorp.com', 'Sarah Johnson', '+1-555-0102', '{"tier": "enterprise", "company": "Acme Corp"}'::jsonb),
    ('test@example.com', 'Test User', '+1-555-0103', '{"tier": "starter"}'::jsonb)
ON CONFLICT (email) DO NOTHING;

-- Sample knowledge base entries for testing
INSERT INTO knowledge_base (title, content, category, embedding) VALUES
    ('Password Reset', 'To reset your password, go to techcorp.com/login and click "Forgot Password?". Enter your email to receive a reset link valid for 1 hour. If you don''t receive the email, check your spam folder.', 'account', NULL),
    ('Billing Inquiry', 'For billing questions, check Settings > Billing in your dashboard. Invoices are available for download. Contact billing@techcorp.com for refund requests.', 'billing', NULL),
    ('Slack Integration', 'To connect Slack, go to Settings > Integrations > Slack and click "Connect". Authenticate with your Slack workspace. Notifications will be sent to your selected channel.', 'integrations', NULL)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- MAINTENANCE FUNCTIONS
-- ============================================================================

-- Function to clean up old conversations (retention policy)
CREATE OR REPLACE FUNCTION cleanup_old_conversations(retention_days INTEGER DEFAULT 365)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Delete messages from old closed conversations
    DELETE FROM messages 
    WHERE conversation_id IN (
        SELECT id FROM conversations 
        WHERE status = 'closed' 
        AND ended_at < NOW() - (retention_days || ' days')::INTERVAL
    );
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Delete old closed conversations
    DELETE FROM conversations 
    WHERE status = 'closed' 
    AND ended_at < NOW() - (retention_days || ' days')::INTERVAL;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to archive resolved tickets
CREATE OR REPLACE FUNCTION archive_resolved_tickets(days_after_resolution INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    archived_count INTEGER;
BEGIN
    UPDATE tickets 
    SET status = 'closed'
    WHERE status = 'resolved'
    AND resolved_at < NOW() - (days_after_resolution || ' days')::INTERVAL;
    
    GET DIAGNOSTICS archived_count = ROW_COUNT;
    RETURN archived_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TABLE 10: notifications
-- ============================================================================
-- Purpose: Store user notifications for read/unread tracking
-- Tracks notifications for new tickets, updates, messages, etc.
-- Supports "Mark as All Read" functionality

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255),  -- Can be null for system-wide notifications
    notification_type VARCHAR(50) NOT NULL,  -- 'NEW_TICKET', 'TICKET_UPDATED', 'NEW_MESSAGE', 'URGENT_TICKET'
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    url VARCHAR(500),  -- Link to related resource
    is_read BOOLEAN DEFAULT FALSE,  -- Read status
    reference_id VARCHAR(100),  -- Reference to related entity (ticket_id, message_id, etc.)
    reference_type VARCHAR(50),  -- Type of reference ('ticket', 'message', 'conversation')
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'
);

-- Indexes for efficient queries
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);
CREATE INDEX idx_notifications_type ON notifications(notification_type);
CREATE INDEX idx_notifications_reference ON notifications(reference_type, reference_id);

-- Composite index for common query pattern (unread notifications for user)
CREATE INDEX idx_notifications_user_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;

COMMENT ON TABLE notifications IS 'User notifications with read/unread tracking';
COMMENT ON COLUMN notifications.is_read IS 'False = unread, True = read';
COMMENT ON COLUMN notifications.read_at IS 'Timestamp when notification was marked as read';
COMMENT ON COLUMN notifications.reference_id IS 'ID of related entity (ticket_id, message_id, etc.)';
COMMENT ON COLUMN notifications.reference_type IS 'Type of related entity: ticket, message, conversation';

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
