# TechCorp Product Documentation

## Table of Contents
1. [Account Setup](#account-setup)
2. [Billing & Subscriptions](#billing--subscriptions)
3. [API Usage](#api-usage)
4. [Integrations](#integrations)
5. [Password Reset](#password-reset)
6. [Team Management](#team-management)
7. [Notifications](#notifications)
8. [File Uploads](#file-uploads)
9. [Reporting & Analytics](#reporting--analytics)
10. [Webhooks](#webhooks)

---

## Account Setup

### Creating a New Account

1. Visit **techcorp.com** and click "Start Free Trial"
2. Enter your work email address
3. Create a secure password (minimum 8 characters, including uppercase, lowercase, number, and special character)
4. Enter your company name and team size
5. Verify your email address via the confirmation link sent to your inbox
6. Complete the onboarding wizard to set up your first workspace

### Workspace Configuration

After account creation, configure your workspace:

- **Workspace Name**: Choose a name that represents your organization
- **Workspace URL**: Customize your subdomain (e.g., yourcompany.techcorp.com)
- **Time Zone**: Set your team's primary time zone for accurate scheduling
- **Default Language**: Select from 25+ supported languages
- **Industry**: Helps us provide relevant templates and suggestions

### Single Sign-On (SSO)

Enterprise customers can enable SSO with:
- Google Workspace
- Microsoft Azure AD
- Okta
- OneLogin
- Custom SAML 2.0 providers

Contact your account manager to enable SSO for your organization.

---

## Billing & Subscriptions

### Payment Methods

We accept the following payment methods:
- Credit/Debit Cards: Visa, MasterCard, American Express, Discover
- PayPal (Business accounts only)
- Bank Transfer (Enterprise annual plans)
- Purchase Orders (Enterprise customers with credit approval)

### Billing Cycle

- **Monthly Billing**: Charged on the same date each month
- **Annual Billing**: Charged once per year with 20% discount
- **Proration**: Upgrades are prorated; downgrades take effect at next billing cycle

### Managing Your Subscription

Access billing settings at **Settings > Billing & Subscription**:

1. **View Current Plan**: See your active plan, next billing date, and amount
2. **Upgrade/Downgrade**: Change plans anytime; prorated charges apply for upgrades
3. **Update Payment Method**: Add or remove payment methods
4. **Download Invoices**: Access all past invoices in PDF format
5. **Cancel Subscription**: Cancel anytime; access continues until end of billing period

### Refund Policy

- Monthly plans: No refunds for partial months
- Annual plans: 30-day money-back guarantee
- Enterprise plans: Custom refund terms per contract

### Failed Payments

If a payment fails:
1. You'll receive an email notification immediately
2. A 7-day grace period begins with continued service access
3. After 7 days, workspace becomes read-only until payment is resolved
4. After 30 days, workspace may be archived per data retention policy

---

## API Usage

### Authentication

All API requests require authentication via Bearer token:

```
Authorization: Bearer YOUR_API_KEY
```

Generate API keys at **Settings > Developer > API Keys**.

### Rate Limits

| Tier | Requests/Hour | Requests/Day |
|------|---------------|--------------|
| Starter | 1,000 | 10,000 |
| Growth | 10,000 | 100,000 |
| Enterprise | 100,000 | 1,000,000 |

Rate limit headers are included in all responses:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Unix timestamp when limit resets

### Base URL

```
https://api.techcorp.com/v1
```

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /projects | List all projects |
| POST | /projects | Create a new project |
| GET | /projects/{id} | Get project details |
| PUT | /projects/{id} | Update a project |
| DELETE | /projects/{id} | Delete a project |
| GET | /tasks | List tasks |
| POST | /tasks | Create a task |
| GET | /users | List team members |
| POST | /webhooks | Register a webhook |

### Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid or missing API key |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Contact support |

### SDKs & Libraries

Official SDKs available for:
- JavaScript/Node.js
- Python
- Ruby
- PHP
- Go
- Java

---

## Integrations

### Available Integrations

TechCorp integrates with 100+ applications across categories:

#### Communication
- Slack
- Microsoft Teams
- Discord
- Zoom
- Google Meet

#### Development
- GitHub
- GitLab
- Bitbucket
- Jira
- Jenkins

#### Productivity
- Google Workspace (Docs, Sheets, Drive, Calendar)
- Microsoft 365 (Word, Excel, OneDrive, Outlook)
- Dropbox
- Box
- Notion

#### CRM & Sales
- Salesforce
- HubSpot
- Pipedrive
- Zendesk

#### Design
- Figma
- Adobe Creative Cloud
- InVision
- Miro

### Connecting an Integration

1. Navigate to **Settings > Integrations**
2. Browse or search for the desired integration
3. Click "Connect"
4. Authenticate with the third-party service
5. Configure sync settings and permissions
6. Click "Save" to activate

### Integration Permissions

Each integration requires specific permissions:
- **Read Access**: View data from connected service
- **Write Access**: Create/update data in connected service
- **Admin Access**: Full management capabilities

Review permissions carefully before authorizing any integration.

### Troubleshooting Integrations

If an integration stops working:
1. Check connection status in **Settings > Integrations**
2. Re-authenticate if token has expired
3. Verify permissions haven't changed
4. Review integration logs for error messages
5. Contact support if issues persist

---

## Password Reset

### Self-Service Password Reset

1. Go to the login page at **techcorp.com/login**
2. Click "Forgot Password?"
3. Enter your registered email address
4. Check your email for a password reset link (valid for 1 hour)
5. Click the link and enter your new password
6. Confirm the new password and click "Reset Password"

### Password Requirements

- Minimum 8 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one number (0-9)
- At least one special character (!@#$%^&*)
- Cannot reuse last 5 passwords

### Admin Password Reset

Workspace admins can reset passwords for team members:

1. Go to **Settings > Team Management**
2. Find the user and click the three-dot menu
3. Select "Reset Password"
4. A reset link will be sent to the user's email

### Two-Factor Authentication (2FA)

Enable 2FA for additional security:

1. Go to **Settings > Security**
2. Click "Enable Two-Factor Authentication"
3. Scan the QR code with your authenticator app (Google Authenticator, Authy, etc.)
4. Enter the 6-digit code from your app
5. Save your backup codes in a secure location

### Account Lockout

After 5 failed login attempts:
- Account is temporarily locked for 15 minutes
- A security notification email is sent
- Contact support if you believe this is an error

---

## Team Management

### Adding Team Members

1. Go to **Settings > Team Management**
2. Click "Invite Member"
3. Enter email address(es) (multiple emails supported, separated by commas)
4. Select role: Admin, Member, or Viewer
5. Optionally add a personal message
6. Click "Send Invitation"

### User Roles & Permissions

| Permission | Admin | Member | Viewer |
|------------|-------|--------|--------|
| Create Projects | ✓ | ✓ | ✗ |
| Edit Projects | ✓ | ✓ | ✗ |
| Delete Projects | ✓ | ✗ | ✗ |
| Invite Members | ✓ | ✗ | ✗ |
| Manage Billing | ✓ | ✗ | ✗ |
| Access Reports | ✓ | ✓ | ✓ |
| View Tasks | ✓ | ✓ | ✓ |
| Create Tasks | ✓ | ✓ | ✗ |
| Assign Tasks | ✓ | ✓ | ✗ |

### Removing Team Members

1. Go to **Settings > Team Management**
2. Find the user in the team list
3. Click the three-dot menu next to their name
4. Select "Remove from Team"
5. Confirm the removal

**Note**: Removed members lose access immediately but their historical contributions remain attributed to them.

### Transferring Ownership

To transfer workspace ownership:

1. Current owner goes to **Settings > Team Management**
2. Select another admin user
3. Click "Transfer Ownership"
4. Confirm the transfer via email verification
5. New owner receives full admin privileges

### Bulk User Management

Enterprise customers can manage users via:
- CSV import/export
- SCIM provisioning
- API endpoints for user management

---

## Notifications

### Notification Types

| Type | Description | Default |
|------|-------------|---------|
| Task Assigned | When a task is assigned to you | On |
| Task Due Soon | Reminder 24 hours before due date | On |
| Task Overdue | Alert when task passes due date | On |
| Mention | When someone mentions you in a comment | On |
| Comment Reply | When someone replies to your comment | On |
| Project Update | When a project you're in is updated | Off |
| Weekly Digest | Summary of your activity every Monday | Off |
| Billing Alerts | Payment confirmations and failures | On |
| Security Alerts | Login from new device, password changes | On |

### Notification Channels

Configure how you receive notifications:

#### Email Notifications
- Instant: Sent immediately when triggered
- Digest: Bundled into daily or weekly summaries
- Configure at **Settings > Notifications > Email**

#### Push Notifications (Mobile)
- Requires TechCorp mobile app installed
- Configure at **Settings > Notifications > Push**
- Can be silenced during "Do Not Disturb" hours

#### In-App Notifications
- Bell icon in top navigation
- Red badge shows unread count
- Click to view notification details

#### Slack Integration
- Receive notifications in Slack channels
- Configure at **Settings > Integrations > Slack**

### Do Not Disturb

Set quiet hours to pause non-urgent notifications:

1. Go to **Settings > Notifications**
2. Enable "Do Not Disturb"
3. Set start and end times
4. Select days of the week to apply
5. Emergency notifications (security, billing) still come through

### Notification Preferences by Project

Customize notifications per project:

1. Open the project
2. Click the three-dot menu > "Notification Settings"
3. Choose: All activity, Important only, or Muted
4. Save preferences

---

## File Uploads

### Supported File Types

TechCorp supports uploading most common file types:

| Category | Formats |
|----------|---------|
| Documents | PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT, MD |
| Images | JPG, JPEG, PNG, GIF, SVG, WEBP, BMP |
| Audio | MP3, WAV, AAC, OGG |
| Video | MP4, MOV, AVI, WMV, WEBM |
| Archives | ZIP, RAR, 7Z, TAR, GZ |
| Code | JS, PY, HTML, CSS, JSON, XML, YAML |

### Storage Limits

| Tier | Storage Per File | Total Storage |
|------|------------------|---------------|
| Starter | 25 MB | 5 GB |
| Growth | 100 MB | 100 GB |
| Enterprise | 1 GB | Unlimited |

### Uploading Files

#### Drag and Drop
1. Open any task or project
2. Drag files directly into the attachment area
3. Release to upload
4. Progress bar shows upload status

#### File Browser
1. Click the paperclip icon
2. Browse and select files from your computer
3. Click "Open" to upload

#### Mobile Upload
1. Tap the attachment icon in the mobile app
2. Choose from camera, photo library, or files
3. Select and confirm upload

### File Previews

TechCorp generates previews for:
- Images (inline preview)
- PDFs (inline viewer)
- Videos (embedded player)
- Code files (syntax-highlighted viewer)
- Office documents (converted to preview format)

### File Versioning

When uploading a file with the same name:
- Previous version is preserved in version history
- Up to 10 versions retained per file
- Restore previous versions anytime
- Version comments supported

### File Sharing

Share files with team members or externally:

1. Click on the uploaded file
2. Click the "Share" button
3. Choose sharing option:
   - Team members (automatic access)
   - Generate shareable link (view or edit permissions)
   - Invite external collaborators via email
4. Set expiration date for external links (optional)

### Deleting Files

1. Click on the file
2. Click the three-dot menu
3. Select "Delete"
4. Confirm deletion

**Note**: Deleted files go to trash for 30 days before permanent deletion. Admins can restore from trash.

---

## Reporting & Analytics

### Available Reports

#### Project Health Report
- Completion percentage
- Tasks on track vs. at risk
- Upcoming milestones
- Resource allocation

#### Team Performance Report
- Tasks completed per member
- Average completion time
- Workload distribution
- Collaboration metrics

#### Time Tracking Report
- Hours logged per project
- Billable vs. non-billable time
- Time estimates vs. actual
- Team member utilization

#### Custom Reports
- Build custom reports with drag-and-drop builder
- Choose metrics, dimensions, and filters
- Save and schedule recurring reports

### Dashboard Widgets

Customize your dashboard with widgets:

- **Task Summary**: Total, completed, overdue tasks
- **Project Progress**: Visual progress bars for active projects
- **Team Activity**: Recent actions from team members
- **Upcoming Deadlines**: Tasks due in next 7 days
- **Workload Chart**: Team capacity visualization
- **Burndown Chart**: Sprint progress tracking

### Export Options

Export reports in multiple formats:
- PDF (formatted for printing)
- CSV (for spreadsheet analysis)
- Excel (with formulas and charts)
- JSON (for API integration)

### Scheduled Reports

Automate report delivery:

1. Create or open a report
2. Click "Schedule"
3. Set frequency: Daily, Weekly, Monthly
4. Choose recipients (team members or external emails)
5. Select format (PDF, CSV, Excel)
6. Click "Save Schedule"

### Analytics API

Access analytics data programmatically:

```
GET /v1/analytics/projects/{id}
GET /v1/analytics/team
GET /v1/analytics/tasks
```

See API documentation for full endpoint list.

---

## Webhooks

### Overview

Webhooks allow TechCorp to send real-time notifications to your application when events occur.

### Supported Events

| Event | Description |
|-------|-------------|
| `task.created` | New task created |
| `task.updated` | Task details modified |
| `task.completed` | Task marked complete |
| `task.deleted` | Task deleted |
| `task.assigned` | Task assigned to user |
| `project.created` | New project created |
| `project.updated` | Project details modified |
| `project.archived` | Project archived |
| `comment.created` | New comment added |
| `file.uploaded` | File attached |
| `user.joined` | New team member joined |
| `user.left` | Team member removed |

### Setting Up a Webhook

1. Go to **Settings > Developer > Webhooks**
2. Click "Add Webhook"
3. Enter your endpoint URL (must use HTTPS)
4. Select events to subscribe to
5. (Optional) Add a secret for payload verification
6. Click "Create Webhook"

### Webhook Payload

Example payload for `task.created`:

```json
{
  "id": "wh_123456789",
  "event": "task.created",
  "created_at": "2025-01-15T10:30:00Z",
  "data": {
    "task": {
      "id": "tsk_987654321",
      "title": "Complete Q1 Report",
      "description": "Prepare quarterly financial report",
      "status": "pending",
      "priority": "high",
      "assignee": {
        "id": "usr_111222333",
        "name": "John Doe",
        "email": "john@company.com"
      },
      "project": {
        "id": "prj_444555666",
        "name": "Q1 Planning"
      },
      "due_date": "2025-01-31T23:59:59Z",
      "created_at": "2025-01-15T10:30:00Z"
    }
  }
}
```

### Signature Verification

Secure your webhook endpoint by verifying signatures:

1. TechCorp sends `X-TechCorp-Signature` header with each request
2. Signature is HMAC-SHA256 of payload using your webhook secret
3. Verify signature before processing:

```python
import hmac
import hashlib

def verify_signature(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

### Retry Policy

If your endpoint fails to respond:
- Initial attempt at event trigger
- Retry after 1 minute
- Retry after 5 minutes
- Retry after 30 minutes
- Retry after 2 hours
- Retry after 6 hours
- After 6 failed attempts, webhook is disabled

### Testing Webhooks

Use the "Test" button in webhook settings to send a sample payload to your endpoint. Check your server logs to verify receipt.

### Webhook Logs

View delivery history at **Settings > Developer > Webhooks > [Webhook Name] > Logs**:
- Timestamp
- Event type
- Response status code
- Response time
- Full request/response payloads

---

## Getting Help

For additional assistance:
- **Help Center**: help.techcorp.com
- **Community Forum**: community.techcorp.com
- **Email Support**: support@techcorp.com
- **Live Chat**: Available in-app during business hours
