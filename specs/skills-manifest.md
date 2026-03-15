# TechCorp Customer Success AI Agent - Skills Manifest

**Version:** 1.0  
**Last Updated:** January 2025  
**Owner:** AI Engineering Team  

---

## Overview

This document defines the core skills that the TechCorp Customer Success AI Agent (Digital FTE) must possess. Each skill is a discrete capability that can be invoked independently or composed with other skills to handle complex customer interactions.

---

## Skill 1: Knowledge Retrieval

| Attribute | Value |
|-----------|-------|
| **Name** | `knowledge_retrieval` |
| **Purpose** | Search and retrieve relevant product documentation to answer customer questions |
| **When to Use** | Customer asks a product-related question that requires factual information from documentation |

### Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | The customer's question or search terms |
| `category_filter` | string | No | Optional category to narrow search (e.g., "billing", "technical", "api") |
| `max_results` | integer | No | Maximum number of results to return (default: 5) |

### Outputs

| Field | Type | Description |
|-------|------|-------------|
| `results` | array | List of relevant documentation snippets |
| `results[].section` | string | Section name where content was found |
| `results[].excerpt` | string | Relevant text excerpt (max 200 chars) |
| `results[].relevance_score` | float | Score from 0.0 to 1.0 indicating match quality |
| `results[].source_file` | string | Source document path |

### Constraints

- Maximum 5 results returned per query
- Only use verified documentation from `/context/` folder
- Do not fabricate information not present in docs
- If no results found, return empty array (do not hallucinate)

### Example

**Input:**
```json
{
  "query": "How do I reset my password?",
  "category_filter": "account",
  "max_results": 3
}
```

**Output:**
```json
{
  "results": [
    {
      "section": "password_reset",
      "excerpt": "Go to techcorp.com/login and click 'Forgot Password?'. Enter your email to receive a reset link valid for 1 hour.",
      "relevance_score": 0.95,
      "source_file": "context/product-docs.md"
    },
    {
      "section": "account_setup",
      "excerpt": "Password requirements: minimum 8 characters, uppercase, lowercase, number, and special character.",
      "relevance_score": 0.72,
      "source_file": "context/product-docs.md"
    },
    {
      "section": "two_factor_authentication",
      "excerpt": "After resetting password, enable 2FA for additional security using Google Authenticator or Authy.",
      "relevance_score": 0.58,
      "source_file": "context/product-docs.md"
    }
  ]
}
```

---

## Skill 2: Sentiment Analysis

| Attribute | Value |
|-----------|-------|
| **Name** | `sentiment_analysis` |
| **Purpose** | Analyze customer emotional state to determine appropriate response tone and escalation needs |
| **When to Use** | **EVERY** single customer message, without exception |

### Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message_text` | string | Yes | The full text of the customer's message |
| `include_context` | boolean | No | Whether to consider conversation history (default: true) |

### Outputs

| Field | Type | Description |
|-------|------|-------------|
| `sentiment_score` | float | Numeric score from 0.0 (very negative) to 1.0 (very positive) |
| `sentiment_label` | string | Categorical label: "positive", "neutral", or "negative" |
| `confidence` | float | Model confidence in the analysis (0.0 to 1.0) |
| `emotional_indicators` | array | List of words/phrases that influenced the score |
| `escalation_recommended` | boolean | True if sentiment < 0.3 |

### Thresholds

| Score Range | Label | Action |
|-------------|-------|--------|
| 0.7 - 1.0 | Positive | Standard handling |
| 0.4 - 0.69 | Neutral | Standard handling |
| 0.3 - 0.39 | Negative | Monitor closely |
| 0.0 - 0.29 | Very Negative | **Trigger escalation consideration** |

### Example

**Input:**
```json
{
  "message_text": "This is the THIRD time I'm contacting support! Your app keeps crashing and nobody seems to care. This is absolutely unacceptable!",
  "include_context": true
}
```

**Output:**
```json
{
  "sentiment_score": 0.08,
  "sentiment_label": "negative",
  "confidence": 0.94,
  "emotional_indicators": [
    "THIRD time",
    "keeps crashing",
    "nobody seems to care",
    "absolutely unacceptable"
  ],
  "escalation_recommended": true
}
```

---

## Skill 3: Escalation Decision

| Attribute | Value |
|-----------|-------|
| **Name** | `escalation_decision` |
| **Purpose** | Determine if a customer issue requires human intervention based on defined rules |
| **When to Use** | **AFTER** generating every response (as a validation step) |

### Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conversation_context` | object | Yes | Full conversation history and current state |
| `sentiment_trend` | array | Yes | List of sentiment scores from conversation |
| `current_message` | string | Yes | The customer's latest message |
| `detected_topics` | array | No | Topics identified in the conversation |

### Outputs

| Field | Type | Description |
|-------|------|-------------|
| `should_escalate` | boolean | True if escalation is required |
| `reason` | string | Specific reason for escalation (or null) |
| `urgency_level` | string | "critical", "high", "medium", or "low" |
| `assigned_team` | string | Target team name (or null) |
| `trigger_keywords` | array | Keywords that triggered the escalation |

### Escalation Rules (from escalation-rules.md)

| Trigger | Urgency | Team |
|---------|---------|------|
| Legal threats (lawyer, lawsuit, BBB) | Critical | Legal Team |
| Security breach (hacked, unauthorized access) | Critical | Security Team |
| Refund/chargeback request | High | Billing Team |
| Pricing negotiation | Medium | Sales Team |
| Explicit human request | Medium | Support Team |
| Sentiment < 0.3 | Medium-High | Senior Support |
| 2+ failed knowledge searches | Medium | Support Team |
| Enterprise customer + technical issue | High | Enterprise Support |

### Example

**Input:**
```json
{
  "conversation_context": {
    "customer_tier": "growth",
    "message_count": 4,
    "previous_escalations": 0
  },
  "sentiment_trend": [0.5, 0.4, 0.3, 0.2],
  "current_message": "I want to talk to a real person. This bot is useless. I'm considering legal action if this isn't resolved.",
  "detected_topics": ["technical_issue", "frustration"]
}
```

**Output:**
```json
{
  "should_escalate": true,
  "reason": "Legal/regulatory inquiry",
  "urgency_level": "critical",
  "assigned_team": "Legal Team",
  "trigger_keywords": ["legal action", "real person"]
}
```

---

## Skill 4: Channel Adaptation

| Attribute | Value |
|-----------|-------|
| **Name** | `channel_adaptation` |
| **Purpose** | Format responses appropriately for the target communication channel |
| **When to Use** | **BEFORE** sending any response to a customer |

### Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `response_text` | string | Yes | The raw response content to format |
| `target_channel` | string | Yes | One of: "email", "whatsapp", "web_form" |
| `customer_name` | string | No | Customer's name for personalization |
| `is_followup` | boolean | No | Whether this is a follow-up message |

### Outputs

| Field | Type | Description |
|-------|------|-------------|
| `formatted_response` | string | Channel-appropriate formatted response |
| `character_count` | integer | Length of formatted response |
| `within_limits` | boolean | True if response meets channel length limits |
| `formatting_applied` | array | List of formatting elements added |

### Channel Limits

| Channel | Max Length | Style | Required Elements |
|---------|------------|-------|-------------------|
| Email | 500 words | Formal | Greeting, signature, contact info |
| WhatsApp | 300 chars (preferred) | Casual | Concise, emoji OK (1-2 max) |
| Web Form | 300 words | Semi-formal | Greeting, sign-off |

### Example

**Input:**
```json
{
  "response_text": "To reset your password, go to the login page and click Forgot Password. Enter your email address and you will receive a reset link within a few minutes. The link is valid for one hour. If you do not receive the email, check your spam folder.",
  "target_channel": "whatsapp",
  "customer_name": "Sarah",
  "is_followup": false
}
```

**Output:**
```json
{
  "formatted_response": "Hi Sarah! 👋 To reset your password: go to techcorp.com/login, click 'Forgot Password', enter your email. You'll get a reset link (valid 1 hour). Check spam if you don't see it!",
  "character_count": 198,
  "within_limits": true,
  "formatting_applied": ["casual_greeting", "emoji", "concise_formatting"]
}
```

---

## Skill 5: Customer Identification

| Attribute | Value |
|-----------|-------|
| **Name** | `customer_identification` |
| **Purpose** | Identify and unify customer identity across all communication channels |
| **When to Use** | **ON EVERY** incoming message (first processing step) |

### Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `email_address` | string | No | Customer's email (from email channel or account lookup) |
| `phone_number` | string | No | Customer's phone (from WhatsApp) |
| `form_submission_id` | string | No | Web form session identifier |
| `provided_name` | string | No | Name customer provided |
| `workspace_domain` | string | No | Customer's workspace subdomain |

### Outputs

| Field | Type | Description |
|-------|------|-------------|
| `unified_customer_id` | string | Unique identifier for this customer |
| `is_returning_customer` | boolean | True if customer has prior interactions |
| `merged_history` | array | Combined conversation history across all channels |
| `identified_channels` | array | List of channels this customer has used |
| `customer_tier` | string | Subscription tier (starter/growth/enterprise) |
| `confidence_score` | float | Confidence in the identification (0.0-1.0) |

### Identity Matching Rules

| Match Type | Confidence | Action |
|------------|------------|--------|
| Exact email match | 1.0 | Definitive match |
| Phone + name match | 0.95 | Definitive match |
| Email domain + name match | 0.85 | Probable match |
| Workspace domain only | 0.7 | Possible match (verify) |

### Example

**Input:**
```json
{
  "email_address": "sarah.johnson@acmecorp.com",
  "phone_number": null,
  "form_submission_id": null,
  "provided_name": "Sarah Johnson",
  "workspace_domain": "acmecorp.techcorp.com"
}
```

**Output:**
```json
{
  "unified_customer_id": "cust_a1b2c3d4e5f6",
  "is_returning_customer": true,
  "merged_history": [
    {
      "channel": "whatsapp",
      "timestamp": "2025-01-20T10:15:00Z",
      "topic": "password_reset"
    },
    {
      "channel": "email",
      "timestamp": "2025-01-20T10:45:00Z",
      "topic": "password_reset_followup"
    }
  ],
  "identified_channels": ["whatsapp", "email"],
  "customer_tier": "growth",
  "confidence_score": 1.0
}
```

---

## Skill Composition

Skills are designed to be composed in a specific order for processing customer interactions:

```
┌─────────────────────────────────────────────────────────────┐
│  Incoming Customer Message                                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Customer Identification Skill                            │
│     → Identify who is contacting us                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Sentiment Analysis Skill                                 │
│     → Understand emotional state                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Knowledge Retrieval Skill                                │
│     → Find relevant information                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Generate Response (LLM)                                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Escalation Decision Skill                                │
│     → Validate if human handoff needed                       │
└─────────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
    ┌─────────────────┐         ┌─────────────────┐
    │ Escalate        │         │ 5. Channel      │
    │ to Human        │         │    Adaptation   │
    └─────────────────┘         │    Skill        │
                                └─────────────────┘
                                        │
                                        ▼
                                ┌─────────────────┐
                                │ Send Response   │
                                └─────────────────┘
```

---

## Skill Versioning

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | January 2025 | Initial release |

---

## Appendix: Skill Interdependencies

| Skill | Depends On | Required By |
|-------|------------|-------------|
| Knowledge Retrieval | None | Response Generation |
| Sentiment Analysis | None | Escalation Decision |
| Escalation Decision | Sentiment Analysis | Response Routing |
| Channel Adaptation | Customer Identification | Response Delivery |
| Customer Identification | None | All other skills |

---

**End of Skills Manifest**
