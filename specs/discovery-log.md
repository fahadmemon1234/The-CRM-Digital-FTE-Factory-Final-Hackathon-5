# TechCorp Customer Success AI Agent - Discovery Log

**Date Created:** January 2025  
**Author:** AI Discovery Session  
**Purpose:** Document findings from context analysis to inform system design

---

## Executive Summary

TechCorp requires a 24/7 Customer Success AI Agent that:
- Handles customer inquiries across **3 channels**: Gmail, WhatsApp, Web Form
- Resolves common issues autonomously using provided knowledge base
- Escalates appropriately based on defined rules
- Maintains channel-specific communication styles
- Tracks all interactions with metadata for analytics

---

## 1. Context File Analysis

### 1.1 Company Profile (`company-profile.md`)

| Attribute | Details |
|-----------|---------|
| **Company** | TechCorp - B2B SaaS |
| **Product** | Project management + team collaboration tool |
| **Founded** | 2020 |
| **Customers** | 5,000+ |
| **Pricing Tiers** | Starter ($29/mo), Growth ($79/mo), Enterprise (custom) |
| **Support Hours** | Human: 9am-6pm EST; AI: 24/7 |
| **Enterprise SLA** | 2-hour response, 24-hour resolution |

**Key AI Implications:**
- AI must handle after-hours inquiries (6pm-9am EST, weekends)
- Enterprise customers require priority handling
- Pricing questions need tier-specific answers

---

### 1.2 Product Documentation (`product-docs.md`)

**10 Core Knowledge Areas:**

| # | Topic | Key Details |
|---|-------|-------------|
| 1 | Account Setup | Email verification, workspace config, SSO (Enterprise) |
| 2 | Billing | 3 payment methods, proration rules, 30-day refund (annual only) |
| 3 | API | Rate limits by tier, Bearer auth, 6 official SDKs |
| 4 | Integrations | 100+ apps across 5 categories |
| 5 | Password Reset | Self-service + admin reset, 2FA setup |
| 6 | Team Management | 3 roles (Admin/Member/Viewer), bulk ops (Enterprise) |
| 7 | Notifications | 9 types, 4 channels, DND scheduling |
| 8 | File Uploads | Size limits by tier (25MB/100MB/1GB), 30-day trash |
| 9 | Reporting | 4 report types, 4 export formats, scheduling |
| 10 | Webhooks | 12 event types, HMAC verification, retry policy |

**AI Knowledge Requirements:**
- Must accurately quote pricing, limits, and policies
- Step-by-step troubleshooting guidance needed
- API technical details for developer queries

---

### 1.3 Escalation Rules (`escalation-rules.md`)

**10 Escalation Triggers:**

| # | Trigger | Priority | Destination |
|---|---------|----------|-------------|
| 1 | Pricing negotiations | Medium | Sales Team |
| 2 | Refund requests | High | Billing Team |
| 3 | Legal threats | Critical | Legal Team |
| 4 | Profanity/abuse | High | Senior Support |
| 5 | Sentiment < 0.3 | Medium-High | Senior Support |
| 6 | Human request | Medium | Support Team |
| 7 | 2 failed searches | Medium | Support Team |
| 8 | Security breach | Critical | Security Team |
| 9 | Enterprise issues | High | Enterprise Support |
| 10 | Repeated contacts | High | Senior Support |

**Escalation Priority Matrix:**

| Priority | Response Time | Triggers |
|----------|---------------|----------|
| Critical | 30 min | Legal threats, Security breach |
| High | 1-2 hours | Refunds, Enterprise, Abuse, Repeated |
| Medium | 4 hours | Pricing, Human request, Failed search |

**AI Decision Logic Required:**
- Sentiment analysis integration
- Keyword/phrase detection
- Customer tier identification
- Conversation history tracking

---

### 1.4 Brand Voice (`brand-voice.md`)

**5 Core Brand Attributes:**
1. Professional but Friendly
2. Knowledgeable but Not Condescending
3. Empathetic and Understanding
4. Solution-Oriented
5. Transparent and Honest

---

## 2. Sample Tickets Analysis (`sample-tickets.json`)

### 2.1 Dataset Overview

| Metric | Value |
|--------|-------|
| **Total Tickets** | 65 |
| **Date Range** | Jan 10-19, 2025 |
| **Channels** | 3 (email, whatsapp, web_form) |
| **Categories** | 5 (billing, technical, general, bug_report, feedback) |

### 2.2 Channel Distribution

| Channel | Count | Percentage |
|---------|-------|------------|
| Email | 22 | 33.8% |
| WhatsApp | 22 | 33.8% |
| Web Form | 21 | 32.3% |

### 2.3 Category Distribution

| Category | Count | Percentage |
|----------|-------|------------|
| Technical | 18 | 27.7% |
| General | 15 | 23.1% |
| Billing | 14 | 21.5% |
| Bug Report | 10 | 15.4% |
| Feedback | 8 | 12.3% |

---

## 3. Channel-Specific Patterns

### 3.1 Email Channel Characteristics

**Structural Patterns:**
- 100% include formal greeting ("Hi", "Dear", "Hello")
- 95% include sign-off ("Best regards", "Thank you", "Cheers")
- 100% include signature with name/company
- 86% have subject lines
- Average length: 150-300 words

**Language Patterns:**
- Complete sentences with proper grammar
- Formal tone ("Could you please help", "I would appreciate")
- Detailed context provided
- Account information often included

**Example (Ticket #1):**
```
Hi TechCorp Team,

I received my invoice for this month and noticed a charge of $79, but I thought 
I was on the Starter plan which should be $29...

My account email is sarah.johnson@acmecorp.com

Thank you for your assistance.

Best regards,
Sarah Johnson
Acme Corporation
```

**AI Response Requirements:**
- Match formal tone
- Include greeting and sign-off
- Provide detailed explanations
- Reference specific account details

---

### 3.2 WhatsApp Channel Characteristics

**Structural Patterns:**
- 0% include greetings or sign-offs
- 100% lowercase or casual capitalization
- 0% have subject lines
- Average length: 10-60 characters
- 9% include emoji (👍)

**Language Patterns:**
- Abbreviated words ("pls", "wanna", "cant")
- Incomplete sentences
- Direct questions without pleasantries
- Urgent/impatient tone common

**Example (Ticket #2):**
```
hey my app keeps crashing when i try to upload files. using iphone. pls help
```

**Example (Ticket #65):**
```
WHY DOES THIS APP KEEP LOGGING ME OUT EVERY 5 MINUTES??? SO ANNOYING!!!
```

**AI Response Requirements:**
- Under 300 characters preferred
- Casual, conversational tone
- Get straight to the point
- Emojis sparingly (1 max)
- May need to split long responses

---

### 3.3 Web Form Channel Characteristics

**Structural Patterns:**
- 100% include subject lines
- 90% include greeting ("Hello", "Hi there")
- 85% include brief sign-off
- Average length: 50-150 words
- More structured than WhatsApp, less formal than email

**Language Patterns:**
- Semi-formal tone
- Complete sentences but conversational
- Context provided but concise
- Specific questions asked

**Example (Ticket #3):**
```
Hello, I'm trying to connect our TechCorp workspace with our Slack channel but 
I'm not seeing the notifications come through. I've followed the setup guide but 
something isn't working. Can you provide some guidance on how to properly 
configure the Slack integration?
```

**AI Response Requirements:**
- Semi-formal, approachable tone
- 2-4 paragraphs typical
- Include relevant links/resources
- Clear action items

---

## 4. Response Format Comparison

| Aspect | Email | WhatsApp | Web Form |
|--------|-------|----------|----------|
| **Greeting** | Required (Dear/Hi/Hello) | Optional (Hi! 👋) | Expected (Hello/Hi there) |
| **Sign-off** | Required (Best regards,) | Optional | Expected |
| **Signature** | Required | Not used | Optional |
| **Length** | No limit (clarity over brevity) | <300 chars preferred | 100-500 chars typical |
| **Formality** | High | Low | Medium |
| **Emojis** | Avoid | 1-2 OK | 1 max |
| **Structure** | Full paragraphs | Short/broken up | 2-4 paragraphs |
| **Links** | Full URLs | Shortened if possible | Full URLs with context |

---

## 5. Common Customer Issue Categories

### 5.1 Billing Issues (14 tickets - 21.5%)

**Sub-types:**
- Unexpected charges (tickets #1, #22)
- Refund requests (tickets #9, #55)
- Plan changes (tickets #5, #26, #50)
- Payment failures (ticket #35)
- Invoice access (ticket #30)
- Pricing inquiries (tickets #15, #39, #41, #43)

**Common Keywords:**
- "charge", "invoice", "refund", "upgrade", "downgrade", "cancel", "payment"

**Escalation Rate:** High (refunds require billing team)

---

### 5.2 Technical Issues (18 tickets - 27.7%)

**Sub-types:**
- Integration problems (tickets #3, #21, #40)
- API questions (tickets #7, #40)
- File upload issues (tickets #2, #18)
- Authentication/SSO (tickets #10, #17, #54)
- Feature not working (tickets #14, #28, #32, #36, #44, #48)
- Performance (ticket #58)

**Common Keywords:**
- "not working", "error", "API", "integration", "sync", "upload"

**Escalation Rate:** Medium (depends on complexity)

---

### 5.3 General Inquiries (15 tickets - 23.1%)

**Sub-types:**
- Account management (tickets #8, #29, #45, #57)
- Data/export requests (tickets #12, #23, #33)
- Training/onboarding (ticket #25)
- Compliance/legal (tickets #19, #49)
- Partnership inquiries (ticket #37)
- Contact requests (ticket #64)

**Common Keywords:**
- "how to", "can I", "question about", "information"

**Escalation Rate:** Low-Medium (depends on request type)

---

### 5.4 Bug Reports (10 tickets - 15.4%)

**Sub-types:**
- Data loss (ticket #4)
- Security concerns (ticket #31)
- UI/display issues (tickets #24, #36)
- App crashes/freezes (tickets #11, #38)
- Notification delays (ticket #46)
- Export corruption (ticket #51)
- Webhook issues (ticket #16)

**Common Keywords:**
- "bug", "issue", "broken", "disappearing", "incorrect", "crash"

**Escalation Rate:** High (engineering involvement often needed)

---

### 5.5 Feedback (8 tickets - 12.3%)

**Sub-types:**
- Feature requests (tickets #6, #27, #34, #42, #47, #59)
- Positive feedback (tickets #13, #20, #52)
- Comprehensive reviews (ticket #61)

**Common Keywords:**
- "suggestion", "feature", "would be great", "love", "improvement"

**Escalation Rate:** Low (mostly informational, forward to product)

---

## 6. Escalation Trigger Patterns in Sample Data

### 6.1 Tickets Requiring Escalation (by trigger)

| Ticket | Channel | Trigger | Priority |
|--------|---------|---------|----------|
| #4 | Email | Data loss + Enterprise | High |
| #9 | Web Form | Refund request | High |
| #17 | WhatsApp | Low sentiment (0.2) | Medium-High |
| #19 | Email | GDPR/legal request | Critical |
| #31 | Email | Security breach + Enterprise | Critical |
| #38 | WhatsApp | Low sentiment (0.2) | Medium-High |
| #43 | Email | Trial extension (pricing) | Medium |
| #55 | Email | Legal threat + refund | Critical |
| #58 | Email | Enterprise performance | High |
| #63 | Web Form | Security concern (permissions) | High |
| #65 | WhatsApp | Low sentiment (0.1) + abuse | High |

### 6.2 Sentiment Distribution

| Sentiment Range | Count | Percentage | Action |
|-----------------|-------|------------|--------|
| 0.0 - 0.3 (Very Negative) | 11 | 16.9% | Escalate |
| 0.3 - 0.5 (Negative) | 15 | 23.1% | Monitor |
| 0.5 - 0.7 (Neutral) | 21 | 32.3% | Normal |
| 0.7 - 1.0 (Positive) | 18 | 27.7% | Normal |

**Low Sentiment Tickets (<0.3):**
- #4 (0.1) - Data loss
- #17 (0.2) - Account recovery
- #31 (0.1) - Security breach
- #35 (0.3) - Payment failed
- #38 (0.2) - App freezing
- #51 (0.3) - CSV export broken
- #55 (0.05) - Legal threat
- #56 (0.3) - Video calls broken
- #58 (0.3) - Performance issues
- #63 (0.2) - Permissions bug
- #65 (0.1) - Session timeout anger

---

## 7. Edge Cases Identified

### 7.1 Empty/Invalid Messages

**Ticket #60:** Empty message via web form
```json
{
  "message": "",
  "channel": "web_form"
}
```

**AI Handling:**
- Request clarification
- Don't assume intent
- May escalate if no response

---

### 7.2 Extremely Long Messages

**Ticket #61:** Comprehensive feedback (400+ words)
- Multiple sections (What we love, Areas for improvement)
- Rating provided (8/10)
- Contact info offered

**AI Handling:**
- Acknowledge all points
- Summarize understanding
- Forward to product team

---

### 7.3 Legal Threats

**Ticket #55:** Formal legal notice
- References previous tickets
- Lists demands
- Threatens chargeback, BBB, legal action
- ALL CAPS emphasis

**AI Handling:**
- Do NOT attempt resolution
- Acknowledge concern
- Escalate immediately to Legal
- Do not admit liability

---

### 7.4 Security Breaches

**Ticket #31:** Unauthorized access report
- Former employee access
- Foreign IP address
- Enterprise customer
- Phone contact requested

**AI Handling:**
- Do NOT ask for passwords
- Provide reassurance
- Escalate to Security Team immediately
- Enterprise SLA applies (30 min)

---

### 7.5 Highly Emotional Messages

**Ticket #65:** ALL CAPS anger
```
WHY DOES THIS APP KEEP LOGGING ME OUT EVERY 5 MINUTES??? SO ANNOYING!!!
```

**AI Handling:**
- Acknowledge frustration
- Apologize sincerely
- Provide immediate solution if known
- Escalate if sentiment < 0.3

---

### 7.6 Multi-Issue Tickets

Some tickets contain multiple issues requiring different handling:
- Billing + cancellation request
- Technical + enterprise priority
- Legal + refund demand

**AI Handling:**
- Identify all triggers
- Escalate to highest-priority destination
- Note all issues in handoff

---

## 8. Questions Requiring Clarification

### 8.1 Channel Integration Questions

| # | Question | Priority |
|---|----------|----------|
| Q1 | What Gmail API authentication method will be used? (OAuth2, service account) | High |
| Q2 | What WhatsApp Business API provider? (Twilio, Meta direct, other) | High |
| Q3 | Where is the web form hosted? What's the submission endpoint? | High |
| Q4 | How should incoming emails be parsed? (HTML, plain text, attachments) | Medium |
| Q5 | Should WhatsApp support multimedia (images, voice notes)? | Medium |

### 8.2 Data Storage Questions

| # | Question | Priority |
|---|----------|----------|
| Q6 | What database system for interaction history? (PostgreSQL, MongoDB) | High |
| Q7 | How long should conversation history be retained? | Medium |
| Q8 | Should conversations be linked to customer accounts? How? | High |
| Q9 | What PII (Personally Identifiable Information) handling requirements? | High |
| Q10 | GDPR data deletion - how to handle historical conversations? | High |

### 8.3 AI/LLM Questions

| # | Question | Priority |
|---|----------|----------|
| Q11 | Which LLM provider? (OpenAI, Anthropic, local) | High |
| Q12 | What's the token budget per conversation? | Medium |
| Q13 | How should the AI handle ambiguous queries? | Medium |
| Q14 | Should conversations span multiple turns or single Q&A? | High |
| Q15 | What's the maximum conversation length before escalation? | Medium |

### 8.4 Escalation Workflow Questions

| # | Question | Priority |
|---|----------|----------|
| Q16 | How should escalations be delivered? (Email, Slack, ticketing system) | High |
| Q17 | What ticketing system is used? (Zendesk, Jira, custom) | Medium |
| Q18 | Should AI continue conversation while waiting for human? | Medium |
| Q19 | How to handle escalations outside business hours? | High |
| Q20 | What's the feedback loop from human agents to AI? | Low |

### 8.5 Monitoring & Analytics Questions

| # | Question | Priority |
|---|----------|----------|
| Q21 | What metrics dashboard is needed? | Medium |
| Q22 | Should there be real-time alerts for escalation spikes? | Medium |
| Q23 | How to track AI resolution rate vs escalation rate? | Medium |
| Q24 | Customer satisfaction survey integration? | Low |
| Q25 | Conversation sampling for quality assurance? | Low |

---

## 9. System Architecture Implications

### 9.1 Required Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     Customer Success AI Agent                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Gmail      │  │   WhatsApp   │  │  Web Form    │          │
│  │   Handler    │  │   Handler    │  │   Handler    │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                   │
│                           │                                     │
│                  ┌────────▼────────┐                            │
│                  │  Message        │                            │
│                  │  Processor      │                            │
│                  └────────┬────────┘                            │
│                           │                                     │
│         ┌─────────────────┼─────────────────┐                  │
│         │                 │                 │                   │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐          │
│  │  Intent      │  │  Sentiment   │  │  Channel     │          │
│  │  Classifier  │  │  Analyzer    │  │  Formatter   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                   │
│                           │                                     │
│                  ┌────────▼────────┐                            │
│                  │  Knowledge      │                            │
│                  │  Base Search    │                            │
│                  └────────┬────────┘                            │
│                           │                                     │
│         ┌─────────────────┼─────────────────┐                  │
│         │                 │                 │                   │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐          │
│  │  Response    │  │  Escalation  │  │  Database    │          │
│  │  Generator   │  │  Detector    │  │  Logger      │          │
│  └──────────────┘  └──────┬───────┘  └──────────────┘          │
│                           │                                     │
│                  ┌────────▼────────┐                            │
│                  │  Human Handoff  │                            │
│                  │  (Email/Slack)  │                            │
│                  └─────────────────┘                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 9.2 Data Flow

1. **Ingestion**: Message received from channel (Gmail/WhatsApp/Web Form)
2. **Normalization**: Convert to standard format with metadata
3. **Analysis**: Classify intent, detect sentiment, identify escalation triggers
4. **Knowledge Search**: Query context files for relevant information
5. **Response Generation**: Create channel-appropriate response
6. **Escalation Check**: Evaluate if escalation is required
7. **Output**: Send response via original channel
8. **Logging**: Store interaction with full metadata

### 9.3 Metadata Schema

```json
{
  "interaction_id": "uuid",
  "timestamp": "ISO8601",
  "channel": "email|whatsapp|web_form",
  "customer": {
    "email": "string",
    "account_id": "string",
    "tier": "starter|growth|enterprise"
  },
  "message": {
    "subject": "string|null",
    "body": "string",
    "word_count": number,
    "has_attachments": boolean
  },
  "analysis": {
    "category": "billing|technical|general|bug_report|feedback",
    "sentiment_score": float,
    "escalation_triggers": ["string"],
    "requires_escalation": boolean
  },
  "response": {
    "body": "string",
    "word_count": number,
    "generated_at": "ISO8601",
    "escalated_to": "team_name|null"
  },
  "resolution": {
    "resolved": boolean,
    "resolution_time_seconds": number,
    "customer_satisfaction": float|null
  }
}
```

---

## 10. Implementation Priorities

### Phase 1: Core Functionality (MVP)
- [ ] Web form handler (simplest channel)
- [ ] Knowledge base search
- [ ] Response generation with brand voice
- [ ] Basic escalation detection
- [ ] Database logging

### Phase 2: Channel Expansion
- [ ] Gmail integration
- [ ] WhatsApp integration
- [ ] Channel-specific formatting
- [ ] Multi-turn conversations

### Phase 3: Advanced Features
- [ ] Sentiment analysis integration
- [ ] Escalation workflow automation
- [ ] Analytics dashboard
- [ ] Customer account linking

### Phase 4: Optimization
- [ ] Conversation quality monitoring
- [ ] AI response accuracy tracking
- [ ] Escalation rate optimization
- [ ] Customer satisfaction surveys

---

## 11. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| AI gives incorrect information | Medium | High | Human review queue, confidence thresholds |
| Escalation missed | Medium | High | Conservative escalation thresholds |
| Brand voice inconsistency | Low | Medium | Response templates, quality checks |
| Channel API rate limits | Medium | Medium | Request queuing, backoff strategies |
| PII data exposure | Low | Critical | Data minimization, encryption, access controls |
| After-hours escalation delays | High | Medium | On-call rotation, clear SLAs |

---

## 12. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| AI Resolution Rate | >85% | Resolved without escalation / Total |
| Escalation Accuracy | >90% | Correct team assignment / Total escalations |
| Response Time | <30 seconds | Average time to first response |
| Customer Satisfaction | >4.0/5.0 | Post-interaction surveys |
| Escalation Rate | <15% | Escalations / Total conversations |
| Brand Voice Compliance | >95% | Quality assurance sampling |

---

## Appendix A: Sample Ticket Analysis by Channel

### Email Tickets (22 total)
- Average word count: 187 words
- 100% have subject lines
- 95% have formal sign-offs
- Common categories: Technical (6), Billing (5), General (5)
- Escalation triggers: 5 (security, legal, enterprise, refunds)

### WhatsApp Tickets (22 total)
- Average word count: 18 words
- 0% have subject lines
- 0% have sign-offs
- Common categories: Technical (6), General (5), Billing (5)
- Escalation triggers: 4 (low sentiment, bugs)

### Web Form Tickets (21 total)
- Average word count: 67 words
- 100% have subject lines
- 70% have brief sign-offs
- Common categories: Technical (6), Billing (4), General (5)
- Escalation triggers: 3 (refunds, security, permissions)

---

## Appendix B: Keyword Triggers for Escalation

### Legal Team
- lawyer, attorney, lawsuit, sue, court
- BBB, Better Business Bureau, FTC
- fraud, unauthorized, legal notice
- GDPR, data deletion, Article 17

### Billing Team
- refund, chargeback, money back
- duplicate charge, unauthorized charge
- cancel and refund

### Security Team
- hacked, breach, unauthorized access
- strange login, compromised
- former employee access

### Senior Support
- sentiment < 0.3
- profanity detected
- "talk to a human", "real person"
- repeated contact (3+ times)

---

**End of Discovery Log**
