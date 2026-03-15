-- ============================================================================
-- TechCorp Customer Success AI Agent - Seed Data
-- ============================================================================
--
-- Purpose: Populate database with demo data for testing and development
-- Usage: psql -U fte_user -d fte_db -f seed.sql
--
-- INCUBATION MAPPING:
-- -------------------
-- Incubation: Hardcoded sample data in Python dicts
-- Production: Normalized seed data with realistic test scenarios
--
-- This seed file includes:
-- - Sample customers with cross-channel identities
-- - Sample conversations with messages
-- - Sample tickets with various statuses
-- - Knowledge base entries with categories
-- - Channel configurations
--
-- Author: AI Engineering Team
-- Version: 1.0.0
-- ============================================================================

-- ============================================================================
-- SEED DATA: CUSTOMERS
-- ============================================================================

INSERT INTO customers (email, name, phone, metadata) VALUES
    -- Enterprise customers
    ('sarah.johnson@acmecorp.com', 'Sarah Johnson', '+1-555-0101', 
     '{"tier": "enterprise", "company": "Acme Corp", "employees": "500-1000"}'::jsonb),
    
    ('michael.chen@techstart.io', 'Michael Chen', '+1-555-0102',
     '{"tier": "growth", "company": "TechStart", "employees": "50-100"}'::jsonb),
    
    ('emma.williams@globalinc.com', 'Emma Williams', '+1-555-0103',
     '{"tier": "enterprise", "company": "Global Inc", "employees": "1000+"}'::jsonb),
    
    -- Growth customers
    ('david.brown@startup.co', 'David Brown', '+1-555-0104',
     '{"tier": "growth", "company": "Startup Co", "employees": "10-50"}'::jsonb),
    
    ('lisa.martinez@innovate.com', 'Lisa Martinez', '+1-555-0105',
     '{"tier": "growth", "company": "Innovate Ltd", "employees": "50-100"}'::jsonb),
    
    -- Starter customers
    ('john.doe@example.com', 'John Doe', '+1-555-0106',
     '{"tier": "starter", "company": "Freelancer"}'::jsonb),
    
    ('jennifer.lee@smallbiz.com', 'Jennifer Lee', '+1-555-0107',
     '{"tier": "starter", "company": "Small Biz", "employees": "1-10"}'::jsonb),
    
    -- Test accounts
    ('test@example.com', 'Test User', '+1-555-0108',
     '{"tier": "starter"}'::jsonb),
    
    ('demo@techcorp.com', 'Demo User', '+1-555-0109',
     '{"tier": "enterprise", "company": "TechCorp", "internal": true}'::jsonb),
    
    ('alex.rivera@company.com', 'Alex Rivera', '+1-555-0110',
     '{"tier": "growth", "company": "Company Inc"}'::jsonb)

ON CONFLICT (email) DO UPDATE SET
    name = EXCLUDED.name,
    phone = EXCLUDED.phone,
    metadata = EXCLUDED.metadata;

-- ============================================================================
-- SEED DATA: CUSTOMER IDENTIFIERS (Cross-channel identity)
-- ============================================================================

INSERT INTO customer_identifiers (customer_id, identifier_type, identifier_value, verified) VALUES
    -- Sarah Johnson - multiple emails and phone
    ((SELECT id FROM customers WHERE email = 'sarah.johnson@acmecorp.com'), 'email', 'sarah.johnson@acmecorp.com', true),
    ((SELECT id FROM customers WHERE email = 'sarah.johnson@acmecorp.com'), 'email', 'sarah@acmecorp.com', true),
    ((SELECT id FROM customers WHERE email = 'sarah.johnson@acmecorp.com'), 'phone', '+1-555-0101', true),
    
    -- Michael Chen - email and WhatsApp
    ((SELECT id FROM customers WHERE email = 'michael.chen@techstart.io'), 'email', 'michael.chen@techstart.io', true),
    ((SELECT id FROM customers WHERE email = 'michael.chen@techstart.io'), 'whatsapp', '+15550102', true),
    
    -- Emma Williams - multiple channels
    ((SELECT id FROM customers WHERE email = 'emma.williams@globalinc.com'), 'email', 'emma.williams@globalinc.com', true),
    ((SELECT id FROM customers WHERE email = 'emma.williams@globalinc.com'), 'phone', '+1-555-0103', true),
    ((SELECT id FROM customers WHERE email = 'emma.williams@globalinc.com'), 'whatsapp', '+15550103', true),
    
    -- David Brown - email only
    ((SELECT id FROM customers WHERE email = 'david.brown@startup.co'), 'email', 'david.brown@startup.co', true),
    
    -- Lisa Martinez - email and WhatsApp
    ((SELECT id FROM customers WHERE email = 'lisa.martinez@innovate.com'), 'email', 'lisa.martinez@innovate.com', true),
    ((SELECT id FROM customers WHERE email = 'lisa.martinez@innovate.com'), 'whatsapp', '+15550105', true),
    
    -- John Doe - email only
    ((SELECT id FROM customers WHERE email = 'john.doe@example.com'), 'email', 'john.doe@example.com', true),
    
    -- Jennifer Lee - email and phone
    ((SELECT id FROM customers WHERE email = 'jennifer.lee@smallbiz.com'), 'email', 'jennifer.lee@smallbiz.com', true),
    ((SELECT id FROM customers WHERE email = 'jennifer.lee@smallbiz.com'), 'phone', '+1-555-0107', true),
    
    -- Test user - all channels
    ((SELECT id FROM customers WHERE email = 'test@example.com'), 'email', 'test@example.com', true),
    ((SELECT id FROM customers WHERE email = 'test@example.com'), 'whatsapp', '+15550108', true),
    
    -- Demo user - all channels
    ((SELECT id FROM customers WHERE email = 'demo@techcorp.com'), 'email', 'demo@techcorp.com', true),
    ((SELECT id FROM customers WHERE email = 'demo@techcorp.com'), 'whatsapp', '+15550109', true),
    
    -- Alex Rivera - email and WhatsApp
    ((SELECT id FROM customers WHERE email = 'alex.rivera@company.com'), 'email', 'alex.rivera@company.com', true),
    ((SELECT id FROM customers WHERE email = 'alex.rivera@company.com'), 'whatsapp', '+15550110', true)

ON CONFLICT (identifier_type, identifier_value) DO NOTHING;

-- ============================================================================
-- SEED DATA: CONVERSATIONS
-- ============================================================================

INSERT INTO conversations (customer_id, initial_channel, started_at, ended_at, status, sentiment_score, resolution_type, escalated_to, metadata) VALUES
    -- Sarah Johnson - Email conversation (resolved)
    ((SELECT id FROM customers WHERE email = 'sarah.johnson@acmecorp.com'), 'email', 
     NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days', 'resolved', 0.85, 
     'resolved_by_ai', NULL, '{"topic": "billing", "satisfaction": "high"}'::jsonb),
    
    -- Michael Chen - WhatsApp conversation (escalated)
    ((SELECT id FROM customers WHERE email = 'michael.chen@techstart.io'), 'whatsapp',
     NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day', 'escalated', 0.25,
     'escalated_to_human', 'Billing Team', '{"topic": "refund", "urgency": "high"}'::jsonb),
    
    -- Emma Williams - Web form conversation (active)
    ((SELECT id FROM customers WHERE email = 'emma.williams@globalinc.com'), 'web_form',
     NOW() - INTERVAL '3 hours', NULL, 'active', 0.65, NULL, NULL, '{"topic": "technical", "product": "API"}'::jsonb),
    
    -- David Brown - Email conversation (resolved)
    ((SELECT id FROM customers WHERE email = 'david.brown@startup.co'), 'email',
     NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days', 'resolved', 0.92,
     'resolved_by_ai', NULL, '{"topic": "integration", "satisfaction": "very_high"}'::jsonb),
    
    -- Lisa Martinez - WhatsApp conversation (closed)
    ((SELECT id FROM customers WHERE email = 'lisa.martinez@innovate.com'), 'whatsapp',
     NOW() - INTERVAL '1 week', NOW() - INTERVAL '1 week', 'closed', 0.78,
     'resolved_by_ai', NULL, '{"topic": "feature_request"}'::jsonb),
    
    -- John Doe - Web form conversation (pending)
    ((SELECT id FROM customers WHERE email = 'john.doe@example.com'), 'web_form',
     NOW() - INTERVAL '1 hour', NULL, 'active', 0.55, NULL, NULL, '{"topic": "general"}'::jsonb),
    
    -- Jennifer Lee - Email conversation (resolved)
    ((SELECT id FROM customers WHERE email = 'jennifer.lee@smallbiz.com'), 'email',
     NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days', 'resolved', 0.88,
     'resolved_by_ai', NULL, '{"topic": "account", "satisfaction": "high"}'::jsonb),
    
    -- Test user - Multi-channel conversation (active)
    ((SELECT id FROM customers WHERE email = 'test@example.com'), 'email',
     NOW() - INTERVAL '2 hours', NULL, 'active', 0.70, NULL, NULL, '{"topic": "testing", "multi_channel": true}'::jsonb),
    
    -- Demo user - WhatsApp conversation (resolved)
    ((SELECT id FROM customers WHERE email = 'demo@techcorp.com'), 'whatsapp',
     NOW() - INTERVAL '6 hours', NOW() - INTERVAL '5 hours', 'resolved', 0.95,
     'resolved_by_ai', NULL, '{"topic": "demo", "internal": true}'::jsonb),
    
    -- Alex Rivera - Web form conversation (escalated)
    ((SELECT id FROM customers WHERE email = 'alex.rivera@company.com'), 'web_form',
     NOW() - INTERVAL '12 hours', NULL, 'escalated', 0.15,
     'escalated_to_human', 'Technical Team', '{"topic": "bug", "severity": "critical"}'::jsonb)

ON CONFLICT DO NOTHING;

-- ============================================================================
-- SEED DATA: MESSAGES
-- ============================================================================

-- Messages for Sarah Johnson's conversation (Email - Billing inquiry)
INSERT INTO messages (conversation_id, channel, direction, role, content, tokens_used, latency_ms, tool_calls, delivery_status) VALUES
    ((SELECT id FROM conversations JOIN customers ON conversations.customer_id = customers.id WHERE customers.email = 'sarah.johnson@acmecorp.com' AND conversations.initial_channel = 'email' ORDER BY started_at DESC LIMIT 1),
     'email', 'inbound', 'customer',
     'Hi, I have a question about my latest invoice. The amount seems higher than expected. Can you help me understand the charges?',
     45, NULL, '[]'::jsonb, 'delivered'),
    
    ((SELECT id FROM conversations JOIN customers ON customers.id = conversations.customer_id WHERE customers.email = 'sarah.johnson@acmecorp.com' AND conversations.initial_channel = 'email' ORDER BY started_at DESC LIMIT 1),
     'email', 'outbound', 'agent',
     'Dear Sarah,

Thank you for reaching out regarding your invoice.

I''d be happy to help you understand the charges. Your latest invoice includes:
- Base plan (Growth): $79/month
- Additional users (5): $25
- Extra storage (50GB): $10
- Total: $114

Is there a specific charge you''d like me to explain in more detail?

Best regards,
TechCorp AI Support Team',
     120, 2450,
     '[{"tool": "search_knowledge_base", "latency_ms": 450}, {"tool": "get_customer_history", "latency_ms": 120}]'::jsonb,
     'delivered'),
    
    ((SELECT id FROM conversations JOIN customers ON customers.id = conversations.customer_id WHERE customers.email = 'sarah.johnson@acmecorp.com' AND conversations.initial_channel = 'email' ORDER BY started_at DESC LIMIT 1),
     'email', 'inbound', 'customer',
     'Oh, I see! I forgot about the additional users. That makes sense now. Thank you for clarifying!',
     35, NULL, '[]'::jsonb, 'delivered'),
    
    ((SELECT id FROM conversations JOIN customers ON customers.id = conversations.customer_id WHERE customers.email = 'sarah.johnson@acmecorp.com' AND conversations.initial_channel = 'email' ORDER BY started_at DESC LIMIT 1),
     'email', 'outbound', 'agent',
     'Dear Sarah,

You''re very welcome! I''m glad I could help clarify the charges.

If you have any other questions in the future, please don''t hesitate to reach out. We''re always here to help!

Best regards,
TechCorp AI Support Team',
     85, 1850,
     '[{"tool": "send_response", "latency_ms": 350}]'::jsonb,
     'delivered');

-- Messages for Michael Chen's conversation (WhatsApp - Refund request, escalated)
INSERT INTO messages (conversation_id, channel, direction, role, content, tokens_used, latency_ms, tool_calls, delivery_status) VALUES
    ((SELECT id FROM conversations JOIN customers ON customers.id = conversations.customer_id WHERE customers.email = 'michael.chen@techstart.io' AND conversations.initial_channel = 'whatsapp' ORDER BY started_at DESC LIMIT 1),
     'whatsapp', 'inbound', 'customer',
     'Hi, I need a refund for my last payment. The service isn''t what we expected.',
     25, NULL, '[]'::jsonb, 'delivered'),
    
    ((SELECT id FROM conversations JOIN customers ON customers.id = conversations.customer_id WHERE customers.email = 'michael.chen@techstart.io' AND conversations.initial_channel = 'whatsapp' ORDER BY started_at DESC LIMIT 1),
     'whatsapp', 'outbound', 'agent',
     'I understand your concern about the service. Let me connect you with our Billing Team who can assist with refund requests. They''ll review your account and get back to you within 2 hours. Reference: BILL-2024-0120',
     65, 3200,
     '[{"tool": "escalate_to_human", "latency_ms": 850}, {"tool": "create_ticket", "latency_ms": 230}]'::jsonb,
     'delivered');

-- Messages for Emma Williams' conversation (Web form - Technical, active)
INSERT INTO messages (conversation_id, channel, direction, role, content, tokens_used, latency_ms, tool_calls, delivery_status) VALUES
    ((SELECT id FROM conversations JOIN customers ON customers.id = conversations.customer_id WHERE customers.email = 'emma.williams@globalinc.com' AND conversations.initial_channel = 'web_form' ORDER BY started_at DESC LIMIT 1),
     'web_form', 'inbound', 'customer',
     'We''re experiencing issues with the API authentication. Our requests are returning 401 errors even though we''re using the correct API key. This is affecting our production environment. Can you please help urgently?',
     55, NULL, '[]'::jsonb, 'delivered'),
    
    ((SELECT id FROM conversations JOIN customers ON customers.id = conversations.customer_id WHERE customers.email = 'emma.williams@globalinc.com' AND conversations.initial_channel = 'web_form' ORDER BY started_at DESC LIMIT 1),
     'web_form', 'outbound', 'agent',
     'Hello Emma,

I understand this is affecting your production environment, and I apologize for the inconvenience.

Let me help you troubleshoot the API authentication issue. Here are the most common causes of 401 errors:

1. **API Key Format**: Ensure you''re including "Bearer " before your API key in the Authorization header
2. **Key Permissions**: Verify your API key has the necessary permissions
3. **Rate Limiting**: Check if you''ve exceeded rate limits

Can you share:
- The exact error message you''re receiving?
- A sample of your request headers (without the actual API key)?
- When did this issue start?

This will help me provide more specific guidance.

Best regards,
TechCorp AI Support Team',
     180, 2850,
     '[{"tool": "search_knowledge_base", "latency_ms": 520}, {"tool": "create_ticket", "latency_ms": 180}]'::jsonb,
     'delivered');

-- ============================================================================
-- SEED DATA: TICKETS
-- ============================================================================

INSERT INTO tickets (conversation_id, customer_id, source_channel, category, priority, status, created_at, resolved_at, resolution_notes) VALUES
    -- Billing inquiry (resolved)
    ((SELECT id FROM conversations JOIN customers ON customers.id = conversations.customer_id WHERE customers.email = 'sarah.johnson@acmecorp.com' ORDER BY started_at DESC LIMIT 1),
     (SELECT id FROM customers WHERE email = 'sarah.johnson@acmecorp.com'),
     'email', 'billing', 'medium', 'resolved',
     NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days',
     'Customer inquiry about invoice charges. Explained additional user fees and storage costs. Customer satisfied with explanation.'),
    
    -- Refund request (escalated)
    ((SELECT id FROM conversations JOIN customers ON customers.id = conversations.customer_id WHERE customers.email = 'michael.chen@techstart.io' ORDER BY started_at DESC LIMIT 1),
     (SELECT id FROM customers WHERE email = 'michael.chen@techstart.io'),
     'whatsapp', 'billing', 'high', 'escalated',
     NOW() - INTERVAL '1 day', NULL,
     'Customer requesting refund. Escalated to Billing Team for review.'),
    
    -- API authentication issue (in progress)
    ((SELECT id FROM conversations JOIN customers ON customers.id = conversations.customer_id WHERE customers.email = 'emma.williams@globalinc.com' ORDER BY started_at DESC LIMIT 1),
     (SELECT id FROM customers WHERE email = 'emma.williams@globalinc.com'),
     'web_form', 'technical', 'high', 'in_progress',
     NOW() - INTERVAL '3 hours', NULL,
     NULL),
    
    -- Integration help (resolved)
    ((SELECT id FROM conversations JOIN customers ON customers.id = conversations.customer_id WHERE customers.email = 'david.brown@startup.co' ORDER BY started_at DESC LIMIT 1),
     (SELECT id FROM customers WHERE email = 'david.brown@startup.co'),
     'email', 'technical', 'low', 'resolved',
     NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days',
     'Helped customer with Slack integration setup. Provided step-by-step guidance. Customer reported successful integration.'),
    
    -- Feature request (closed)
    ((SELECT id FROM conversations JOIN customers ON customers.id = conversations.customer_id WHERE customers.email = 'lisa.martinez@innovate.com' ORDER BY started_at DESC LIMIT 1),
     (SELECT id FROM customers WHERE email = 'lisa.martinez@innovate.com'),
     'whatsapp', 'feedback', 'low', 'closed',
     NOW() - INTERVAL '1 week', NOW() - INTERVAL '1 week',
     'Customer requested dark mode feature. Logged as feature request FR-2024-042. Product team will review.'),
    
    -- General question (open)
    ((SELECT id FROM conversations JOIN customers ON customers.id = conversations.customer_id WHERE customers.email = 'john.doe@example.com' ORDER BY started_at DESC LIMIT 1),
     (SELECT id FROM customers WHERE email = 'john.doe@example.com'),
     'web_form', 'general', 'medium', 'open',
     NOW() - INTERVAL '1 hour', NULL,
     NULL),
    
    -- Account access (resolved)
    ((SELECT id FROM conversations JOIN customers ON customers.id = conversations.customer_id WHERE customers.email = 'jennifer.lee@smallbiz.com' ORDER BY started_at DESC LIMIT 1),
     (SELECT id FROM customers WHERE email = 'jennifer.lee@smallbiz.com'),
     'email', 'technical', 'medium', 'resolved',
     NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days',
     'Customer unable to login. Reset password and verified email. Issue resolved.'),
    
    -- Critical bug (escalated)
    ((SELECT id FROM conversations JOIN customers ON customers.id = conversations.customer_id WHERE customers.email = 'alex.rivera@company.com' ORDER BY started_at DESC LIMIT 1),
     (SELECT id FROM customers WHERE email = 'alex.rivera@company.com'),
     'web_form', 'bug_report', 'critical', 'escalated',
     NOW() - INTERVAL '12 hours', NULL,
     'Customer reporting data loss issue. Escalated to Technical Team with critical priority. Ticket BUG-2024-089.');

-- ============================================================================
-- SEED DATA: KNOWLEDGE BASE
-- ============================================================================

INSERT INTO knowledge_base (title, content, category, embedding) VALUES
    ('Password Reset',
     'To reset your password:
1. Go to techcorp.com/login
2. Click "Forgot Password?"
3. Enter your email address
4. Check your email for reset link (valid for 1 hour)
5. Click the link and enter your new password
6. Your password must be at least 8 characters with one uppercase letter and one number

If you don''t receive the email within 5 minutes, check your spam folder. Contact support if you still have issues.',
     'account', NULL),
    
    ('Two-Factor Authentication (2FA)',
     'Enable 2FA for enhanced security:
1. Go to Settings > Security
2. Click "Enable 2FA"
3. Scan the QR code with your authenticator app (Google Authenticator, Authy, etc.)
4. Enter the 6-digit code from your app
5. Save your backup codes in a secure location

Once enabled, you''ll need to enter a code from your authenticator app each time you log in.',
     'security', NULL),
    
    ('API Authentication',
     'Authenticate API requests using Bearer tokens:

Headers:
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json

Generate API keys in Settings > API Keys.

Rate Limits:
- Starter: 100 requests/minute
- Growth: 500 requests/minute
- Enterprise: 2000 requests/minute

If you receive 401 errors:
1. Verify your API key is correct
2. Ensure you''re including "Bearer " before the key
3. Check that your key hasn''t expired
4. Verify your account is in good standing',
     'api', NULL),
    
    ('Slack Integration',
     'Connect TechCorp to your Slack workspace:
1. Go to Settings > Integrations > Slack
2. Click "Connect to Slack"
3. Authorize the TechCorp app in your Slack workspace
4. Select which Slack channel should receive notifications
5. Configure notification preferences:
   - New tickets
   - Ticket updates
   - Escalations
   - Daily summaries

You can disconnect anytime from the same settings page.',
     'integrations', NULL),
    
    ('Billing and Invoices',
     'View and manage your billing:
1. Go to Settings > Billing
2. View current and past invoices
3. Update payment method
4. Change subscription plan

Invoice includes:
- Base plan fee
- Additional user costs ($5/user/month on Growth, $3 on Enterprise)
- Extra storage ($0.20/GB/month)
- Overage charges (if applicable)

Invoices are generated on the 1st of each month. Payment is automatically charged to your saved payment method within 3 business days.',
     'billing', NULL),
    
    ('User Management',
     'Add or remove team members:
1. Go to Settings > Team
2. Click "Add User"
3. Enter their email address
4. Select their role (Admin, Member, Viewer)
5. They''ll receive an invitation email

User limits by plan:
- Starter: Up to 10 users
- Growth: Up to 50 users
- Enterprise: Unlimited users

Removing a user:
1. Go to Settings > Team
2. Find the user
3. Click the three dots menu
4. Select "Remove User"
5. Confirm removal

Removed users lose access immediately but their data is preserved.',
     'account', NULL),
    
    ('Data Export',
     'Export your data anytime:
1. Go to Settings > Data
2. Click "Export Data"
3. Select what to export:
   - Conversations
   - Tickets
   - Analytics
   - All data
4. Choose format (CSV or JSON)
5. Click "Export"

Large exports may take several minutes. You''ll receive an email when your export is ready for download.

Exports include:
- All conversations with timestamps
- Message content and metadata
- Ticket details and status
- Customer information
- Analytics data',
     'account', NULL),
    
    ('Webhook Configuration',
     'Set up webhooks for real-time updates:
1. Go to Settings > Webhooks
2. Click "Add Webhook"
3. Enter your endpoint URL
4. Select events to subscribe:
   - ticket.created
   - ticket.updated
   - ticket.resolved
   - message.received
   - message.sent
5. Save and copy your webhook secret

Verify webhook signatures using the secret in your endpoint code.

Webhook payload format:
{
  "event": "ticket.created",
  "timestamp": "2024-01-20T12:00:00Z",
  "data": { ... }
}',
     'api', NULL),
    
    ('Troubleshooting Common Issues',
     'Login Issues:
- Reset password using "Forgot Password?"
- Clear browser cache and cookies
- Try incognito/private browsing mode
- Check if your account is active

API Issues:
- Verify API key format (include "Bearer ")
- Check rate limits in your dashboard
- Review API status at status.techcorp.com
- Test with our API explorer tool

Performance Issues:
- Clear browser cache
- Check your internet connection
- Try a different browser
- Contact support if issues persist

Billing Issues:
- Review invoices in Settings > Billing
- Check payment method is up to date
- Contact billing@techcorp.com for refund requests',
     'support', NULL),
    
    ('Mobile App',
     'Access TechCorp on mobile:
1. Download the app:
   - iOS: App Store (search "TechCorp")
   - Android: Google Play Store
2. Log in with your account credentials
3. Enable push notifications for real-time updates

Mobile app features:
- View and respond to tickets
- Real-time notifications
- Offline mode (view cached data)
- Quick reply templates
- Voice-to-text responses

The mobile app syncs with your web account, so you can switch between devices seamlessly.',
     'mobile', NULL);

-- ============================================================================
-- SEED DATA: CHANNEL CONFIGS
-- ============================================================================

INSERT INTO channel_configs (channel, enabled, config, response_template, max_response_length) VALUES
    ('email', true,
     '{"smtp_host": "smtp.techcorp.com", "smtp_port": 587, "from_address": "support@techcorp.com", "reply_to": "noreply@techcorp.com"}'::jsonb,
     'Dear {{customer_name}},

Thank you for reaching out to TechCorp Support.

{{response}}

If you have any other questions, please don''t hesitate to reply to this email.

Best regards,
TechCorp AI Support Team
support@techcorp.com

---
Ticket Reference: {{ticket_id}}
This response was generated by our AI assistant. For complex issues, you can request human support.',
     3000),
    
    ('whatsapp', true,
     '{"api_provider": "twilio", "phone_number": "+14155238886", "sandbox_mode": true}'::jsonb,
     '{{response}}

📱 Reply for more help or type ''human'' for live support.',
     1600),
    
    ('web_form', true,
     '{"form_endpoint": "/api/support/submit", "notification_email": "support@techcorp.com", "auto_reply": true}'::jsonb,
     'Hello {{customer_name}},

Thanks for contacting TechCorp Support.

{{response}}

---
Need more help? Reply to this message or visit our support portal.

Best,
TechCorp Support
support@techcorp.com',
     2000)

ON CONFLICT (channel) DO UPDATE SET
    enabled = EXCLUDED.enabled,
    config = EXCLUDED.config,
    response_template = EXCLUDED.response_template,
    max_response_length = EXCLUDED.max_response_length;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Show summary of seeded data
SELECT 
    'customers' as table_name, 
    COUNT(*) as row_count 
FROM customers
UNION ALL
SELECT 'customer_identifiers', COUNT(*) FROM customer_identifiers
UNION ALL
SELECT 'conversations', COUNT(*) FROM conversations
UNION ALL
SELECT 'messages', COUNT(*) FROM messages
UNION ALL
SELECT 'tickets', COUNT(*) FROM tickets
UNION ALL
SELECT 'knowledge_base', COUNT(*) FROM knowledge_base
UNION ALL
SELECT 'channel_configs', COUNT(*) FROM channel_configs;

-- Show sample customers
SELECT 
    email, 
    name, 
    phone,
    metadata->>'tier' as tier,
    metadata->>'company' as company
FROM customers
ORDER BY created_at DESC
LIMIT 5;

-- Show conversation statistics
SELECT 
    c.status,
    COUNT(*) as count,
    AVG(c.sentiment_score)::numeric(3,2) as avg_sentiment
FROM conversations c
GROUP BY c.status;

-- Show ticket distribution
SELECT 
    t.category,
    t.priority,
    COUNT(*) as count
FROM tickets t
GROUP BY t.category, t.priority
ORDER BY t.category, t.priority;

-- ============================================================================
-- END OF SEED DATA
-- ============================================================================
