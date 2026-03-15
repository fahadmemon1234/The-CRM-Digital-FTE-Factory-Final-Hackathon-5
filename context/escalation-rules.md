# TechCorp Escalation Rules

## Overview

This document defines the rules and procedures for escalating customer inquiries from the AI Customer Success Agent to human support teams. The goal is to ensure customers receive appropriate assistance while maximizing AI resolution rates.

---

## Escalation Triggers

The AI agent should escalate a ticket when ANY of the following conditions are met:

### 1. Pricing Negotiations

**Trigger**: Customer requests discounts, custom pricing, or price matching.

**Keywords and Phrases**:
- "Can you give me a discount?"
- "Is there any flexibility on pricing?"
- "Your competitor offers lower prices"
- "We need a better deal"
- "Can you match [competitor]'s pricing?"
- "What's the best price you can offer?"
- "We're a nonprofit/student startup"
- "Budget constraints"

**Action**: Escalate to **Sales Team**

**Priority**: Medium

**Notes**: AI should provide standard pricing information first, then escalate if customer continues negotiation.

---

### 2. Refund Requests

**Trigger**: Customer requests a refund, chargeback, or cancellation with money back.

**Keywords and Phrases**:
- "I want a refund"
- "Cancel and refund my subscription"
- "Chargeback"
- "Reverse the charge"
- "Money back"
- "This was a mistake, give me my money back"
- "I didn't authorize this charge"
- "Unauthorized transaction"

**Action**: Escalate to **Billing Team**

**Priority**: High (especially if chargeback is mentioned)

**Notes**: AI can explain refund policy first (30-day guarantee for annual plans, no refunds for monthly), but must escalate if customer insists.

---

### 3. Legal Threats

**Trigger**: Customer mentions legal action, lawyers, lawsuits, or regulatory complaints.

**Keywords and Phrases**:
- "Lawyer"
- "Attorney"
- "Lawsuit"
- "Legal action"
- "Sue"
- "Court"
- "Better Business Bureau"
- "BBB complaint"
- "FTC complaint"
- "Consumer protection"
- "Fraud"
- "Unauthorized charges"
- "Govern yourself accordingly"
- "Legal notice"
- "Demand letter"

**Action**: Escalate to **Legal Team** immediately

**Priority**: Critical

**Notes**: AI should NOT attempt to resolve. Acknowledge concern and escalate immediately. Do not admit liability or make promises.

---

### 4. Profanity and Abusive Language

**Trigger**: Customer uses profanity, insults, or abusive language.

**Detection**:
- Explicit profanity (f-bomb, s-word, etc.)
- Personal insults ("you're incompetent", "this is stupid")
- Threatening language ("I'll destroy your company")
- Harassment or discriminatory language

**Action**: Escalate to **Senior Support**

**Priority**: High

**Notes**: AI should remain professional and not engage with abusive content. One warning may be given before escalation.

---

### 5. Low Sentiment Score

**Trigger**: Sentiment analysis score falls below 0.3 (on a scale of 0-1).

**Sentiment Ranges**:
- 0.0 - 0.3: Very Negative → Escalate
- 0.3 - 0.5: Negative → Consider escalation if combined with other triggers
- 0.5 - 0.7: Neutral → Handle normally
- 0.7 - 1.0: Positive → Handle normally

**Action**: Escalate to **Senior Support**

**Priority**: Medium to High (based on exact score)

**Notes**: Sentiment should be evaluated in context. A frustrated but reasonable customer may have low sentiment but not require escalation.

---

### 6. Explicit Human Request

**Trigger**: Customer explicitly requests to speak with a human.

**Keywords and Phrases**:
- "I want to talk to a human"
- "Get me a real person"
- "Speak to someone who understands"
- "This bot is useless"
- "Human agent please"
- "Real support"
- "Not a robot"
- "Actual person"

**Action**: Escalate to **Support Team** (general queue)

**Priority**: Medium

**Notes**: AI can offer to try to help once before escalating, but must respect customer's wishes if they insist.

---

### 7. Failed Search Attempts

**Trigger**: AI cannot find relevant information after 2 consecutive search attempts.

**Conditions**:
- First search returns no relevant results
- AI rephrases and searches again
- Second search also returns no relevant results

**Action**: Escalate to **Support Team**

**Priority**: Medium

**Notes**: AI should inform customer: "I'm having trouble finding the specific information you need. Let me connect you with a team member who can help."

---

### 8. Security Breach Concerns

**Trigger**: Customer reports unauthorized access, data breach, or security vulnerability.

**Keywords and Phrases**:
- "Unauthorized access"
- "Someone hacked my account"
- "Security breach"
- "Data leak"
- "My account was compromised"
- "Strange login activity"
- "Account takeover"

**Action**: Escalate to **Security Team** (urgent)

**Priority**: Critical

**Notes**: AI should NOT ask for sensitive information like passwords. Provide basic reassurance and escalate immediately.

---

### 9. Enterprise Customer Issues

**Trigger**: Customer is on Enterprise plan and reports significant issues.

**Identification**:
- Account ID starts with "ENT-"
- Email domain matches known enterprise customers
- Customer self-identifies as enterprise

**Issues Requiring Escalation**:
- Performance degradation
- SSO/authentication problems
- Data loss concerns
- SLA violations

**Action**: Escalate to **Enterprise Support Team**

**Priority**: High

**Notes**: Enterprise customers have dedicated support with 2-hour response SLA.

---

### 10. Repeated Contact for Same Issue

**Trigger**: Customer has contacted support 3+ times about the same unresolved issue.

**Detection**:
- Check ticket history for similar subjects
- Customer mentions "I've already contacted support multiple times"
- Ticket references previous case numbers

**Action**: Escalate to **Senior Support**

**Priority**: High

**Notes**: This indicates the issue wasn't properly resolved. Senior support should review entire history.

---

## Escalation Destinations

### Billing Team
**Email**: billing@techcorp.com
**Hours**: Monday-Friday, 9 AM - 6 PM EST
**Response SLA**: 4 hours

**Handles**:
- Refund requests
- Payment issues
- Subscription changes
- Invoice disputes
- Pricing inquiries (standard)

---

### Sales Team
**Email**: sales@techcorp.com
**Hours**: Monday-Friday, 9 AM - 6 PM EST
**Response SLA**: 2 hours

**Handles**:
- Pricing negotiations
- Custom quotes
- Enterprise inquiries
- Partnership requests
- Upgrade consultations

---

### Legal Team
**Email**: legal@techcorp.com
**Hours**: Monday-Friday, 9 AM - 5 PM EST
**Response SLA**: 1 hour (urgent), 24 hours (standard)

**Handles**:
- Legal threats
- GDPR/data privacy requests
- Terms of service questions
- Contract disputes
- Regulatory inquiries

---

### Security Team
**Email**: security@techcorp.com
**Hours**: 24/7 (Enterprise customers)
**Response SLA**: 30 minutes (critical), 2 hours (high)

**Handles**:
- Account breaches
- Unauthorized access
- Data leaks
- Security vulnerabilities
- SSO/authentication issues

---

### Senior Support
**Email**: senior-support@techcorp.com
**Hours**: Monday-Friday, 8 AM - 8 PM EST
**Response SLA**: 1 hour

**Handles**:
- Abusive customers
- Complex technical issues
- Repeated contacts
- Low sentiment escalations
- AI fallback cases

---

### Enterprise Support
**Email**: enterprise-support@techcorp.com
**Hours**: 24/7
**Response SLA**: 30 minutes

**Handles**:
- All Enterprise customer issues
- SLA violations
- Dedicated account manager requests
- Custom integrations
- Priority technical support

---

## Escalation Workflow

### Step 1: Identify Trigger
AI detects one or more escalation triggers during conversation.

### Step 2: Gather Context
AI compiles relevant information:
- Customer account details
- Conversation history
- Trigger reason(s)
- Sentiment score
- Previous tickets (if any)

### Step 3: Inform Customer
AI notifies customer: "I want to make sure you get the best assistance. Let me connect you with a team member who specializes in this area."

### Step 4: Create Escalation Ticket
AI generates ticket with:
- Priority level
- Assigned team
- Full conversation transcript
- Trigger classification
- Customer context

### Step 5: Handoff
AI provides customer with:
- Expected response time
- Ticket reference number
- Contact method for follow-up

---

## Escalation Priority Matrix

| Trigger | Priority | Response Time | Team |
|---------|----------|---------------|------|
| Legal Threat | Critical | 30 min | Legal |
| Security Breach | Critical | 30 min | Security |
| Enterprise Issue | High | 1 hour | Enterprise Support |
| Refund/Chargeback | High | 2 hours | Billing |
| Abusive Language | High | 1 hour | Senior Support |
| Repeated Contact | High | 1 hour | Senior Support |
| Low Sentiment (<0.3) | Medium-High | 2 hours | Senior Support |
| Human Request | Medium | 4 hours | Support |
| Failed Search (2x) | Medium | 4 hours | Support |
| Pricing Negotiation | Medium | 4 hours | Sales |

---

## De-escalation Guidelines

AI should attempt de-escalation when:
- Customer is frustrated but not abusive
- Issue is within AI's capability to resolve
- Sentiment is between 0.3-0.5

**De-escalation Techniques**:
1. Acknowledge the frustration: "I understand this is frustrating..."
2. Apologize sincerely: "I'm sorry you're experiencing this..."
3. Take ownership: "Let me help you resolve this..."
4. Provide clear next steps: "Here's what I'll do..."
5. Set expectations: "This should take about X minutes..."

If de-escalation fails after 2 attempts, proceed with escalation.

---

## After-Hours Handling

### Business Hours: 9 AM - 6 PM EST, Monday-Friday

**During Business Hours**:
- All escalations processed immediately
- Teams notified via Slack + email

**After Business Hours**:
- Critical escalations (Security, Legal threats): Page on-call
- High priority: Queue for next business day, send acknowledgment
- Medium priority: Queue for next business day

**Weekend Handling**:
- Enterprise Support: 24/7 coverage maintained
- Security: On-call rotation
- All other teams: Next business day response

---

## Metrics and Monitoring

### Escalation Rate
- Target: <15% of all conversations
- Alert threshold: >20% for any 24-hour period

### Escalation Accuracy
- Target: >90% correct team assignment
- Reviewed weekly by support leadership

### Response Time Compliance
- Target: >95% within SLA
- Tracked per team

### Customer Satisfaction Post-Escalation
- Target: >4.0/5.0 average rating
- Survey sent after resolution

---

## Review and Updates

This document is reviewed:
- Monthly by Support Operations
- Quarterly by Customer Success Leadership
- After any major incident

Last Updated: January 2025
Next Review: February 2025
Owner: VP of Customer Success
