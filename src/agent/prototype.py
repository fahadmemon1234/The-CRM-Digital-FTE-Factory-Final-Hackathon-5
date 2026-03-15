"""
TechCorp Customer Success AI Agent Prototype v2
With conversation memory, state tracking, and cross-channel identity.

Features:
- Full conversation history per customer
- State tracking (sentiment, topics, resolution status)
- Cross-channel identity recognition via email
- Context-aware responses for follow-up questions
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class Channel(Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"


class ResolutionStatus(Enum):
    OPEN = "open"
    SOLVED = "solved"
    PENDING = "pending"
    ESCALATED = "escalated"


@dataclass
class Message:
    """A single message in a conversation."""
    role: str  # "customer" or "agent"
    content: str
    channel: Channel
    timestamp: str
    subject: Optional[str] = None


@dataclass
class ConversationState:
    """Tracks the state of a customer conversation."""
    customer_email: str
    customer_name: Optional[str] = None
    original_channel: Optional[Channel] = None
    channel_switches: List[Channel] = field(default_factory=list)
    messages: List[Message] = field(default_factory=list)
    topics_discussed: List[str] = field(default_factory=list)
    resolution_status: ResolutionStatus = ResolutionStatus.OPEN
    escalation_team: Optional[str] = None
    escalation_reason: Optional[str] = None
    sentiment_history: List[float] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    @property
    def current_sentiment(self) -> float:
        """Calculate average sentiment across conversation."""
        if not self.sentiment_history:
            return 0.5
        return sum(self.sentiment_history) / len(self.sentiment_history)
    
    @property
    def message_count(self) -> int:
        """Total messages in conversation."""
        return len(self.messages)
    
    @property
    def channels_used(self) -> List[str]:
        """Unique channels used in conversation."""
        return list(set(ch.value for ch in self.channel_switches))
    
    def to_dict(self) -> Dict:
        """Convert state to dictionary for serialization."""
        return {
            "customer_email": self.customer_email,
            "customer_name": self.customer_name,
            "original_channel": self.original_channel.value if self.original_channel else None,
            "channel_switches": [ch.value for ch in self.channel_switches],
            "channels_used": list(set(ch.value for ch in self.channel_switches)),
            "total_messages": self.message_count,
            "messages": [
                {
                    "role": m.role,
                    "content": m.content[:200] + "..." if len(m.content) > 200 else m.content,
                    "channel": m.channel.value,
                    "timestamp": m.timestamp,
                    "subject": m.subject
                }
                for m in self.messages
            ],
            "topics_discussed": self.topics_discussed,
            "resolution_status": self.resolution_status.value,
            "escalation_team": self.escalation_team,
            "escalation_reason": self.escalation_reason,
            "sentiment_history": self.sentiment_history,
            "current_sentiment": self.current_sentiment,
            "is_escalated": self.resolution_status == ResolutionStatus.ESCALATED,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


@dataclass
class CustomerMessage:
    """Incoming customer message."""
    channel: Channel
    message: str
    subject: Optional[str] = None
    customer_email: Optional[str] = None
    customer_name: Optional[str] = None
    timestamp: Optional[str] = None


@dataclass
class AgentResponse:
    """Agent response with metadata."""
    response: str
    escalation_needed: bool
    escalation_reason: Optional[str]
    escalation_team: Optional[str]
    channel: Channel
    context_aware: bool = False
    is_followup: bool = False


class SentimentAnalyzer:
    """Simple sentiment analysis based on keywords."""
    
    POSITIVE_WORDS = [
        'great', 'excellent', 'amazing', 'love', 'thank', 'thanks', 'awesome',
        'wonderful', 'fantastic', 'helpful', 'appreciate', 'happy', 'pleased',
        'good', 'nice', 'perfect', 'best', 'commend', 'recommend'
    ]
    
    NEGATIVE_WORDS = [
        'hate', 'terrible', 'awful', 'horrible', 'worst', 'angry', 'frustrated',
        'annoying', 'useless', 'broken', 'disappointed', 'unhappy', 'issue',
        'problem', 'crash', 'error', 'fail', 'wrong', 'bad', 'sucks', 'stupid'
    ]
    
    INTENSIFIERS = ['very', 'really', 'extremely', 'absolutely', 'totally', 'completely']
    
    def analyze(self, text: str) -> float:
        """
        Analyze sentiment of text.
        Returns score from 0.0 (very negative) to 1.0 (very positive).
        """
        text_lower = text.lower()
        words = text_lower.split()
        
        positive_count = sum(1 for word in self.POSITIVE_WORDS if word in text_lower)
        negative_count = sum(1 for word in self.NEGATIVE_WORDS if word in text_lower)
        
        # Check for intensifiers
        has_intensifier = any(intensifier in text_lower for intensifier in self.INTENSIFIERS)
        if has_intensifier:
            negative_count *= 1.5  # Intensifiers amplify negative sentiment more
        
        # Check for caps (indicates strong emotion)
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > 0.3:  # More than 30% caps
            negative_count *= 1.5  # Assume shouting is negative
        
        total = positive_count + negative_count
        if total == 0:
            return 0.5  # Neutral
        
        # Calculate score (0.0 to 1.0)
        score = positive_count / total
        return round(score, 2)


class ConversationManager:
    """Manages conversations across channels for all customers."""
    
    def __init__(self):
        # Key: customer email, Value: ConversationState
        self.conversations: Dict[str, ConversationState] = {}
    
    def get_or_create(self, customer_email: str) -> ConversationState:
        """Get existing conversation or create new one."""
        if customer_email not in self.conversations:
            self.conversations[customer_email] = ConversationState(
                customer_email=customer_email
            )
        return self.conversations[customer_email]
    
    def add_message(self, state: ConversationState, message: Message):
        """Add a message to conversation history."""
        state.messages.append(message)
        state.updated_at = datetime.utcnow().isoformat()
        
        # Track channel switches
        if message.channel not in state.channel_switches:
            state.channel_switches.append(message.channel)
        
        # Set original channel if not set
        if state.original_channel is None:
            state.original_channel = message.channel
    
    def get_context(self, state: ConversationState, max_messages: int = 5) -> str:
        """Get conversation context for generating responses."""
        if not state.messages:
            return ""
        
        recent = state.messages[-max_messages:]
        context_parts = []
        
        for msg in recent:
            channel_str = f"[{msg.channel.value}]"
            if msg.subject:
                context_parts.append(f"{channel_str} {msg.role}: {msg.subject} - {msg.content[:100]}")
            else:
                context_parts.append(f"{channel_str} {msg.role}: {msg.content[:100]}")
        
        return "\n".join(context_parts)
    
    def extract_topics(self, text: str) -> List[str]:
        """Extract topics from message text."""
        topics = []
        text_lower = text.lower()
        
        topic_keywords = {
            'billing': ['invoice', 'charge', 'payment', 'bill', 'refund', 'pricing', 'cost'],
            'technical': ['bug', 'crash', 'error', 'not working', 'broken', 'issue'],
            'account': ['password', 'login', 'account', 'email', '2fa', 'authentication'],
            'integration': ['slack', 'salesforce', 'integration', 'sync', 'connect'],
            'feature': ['feature request', 'suggestion', 'would be great', 'add'],
            'file_upload': ['upload', 'file', 'attachment', 'document'],
            'notification': ['notification', 'email notification', 'alert', 'reminder'],
            'api': ['api', 'endpoint', 'rate limit', 'webhook'],
        }
        
        for topic, keywords in topic_keywords.items():
            if any(kw in text_lower for kw in keywords):
                topics.append(topic)
        
        return topics
    
    def update_state(self, state: ConversationState, sentiment: float, 
                     escalation_needed: bool, escalation_team: Optional[str]):
        """Update conversation state based on new message."""
        # Update sentiment
        state.sentiment_history.append(sentiment)
        
        # Update resolution status
        if escalation_needed:
            state.resolution_status = ResolutionStatus.ESCALATED
            state.escalation_team = escalation_team
        elif state.resolution_status != ResolutionStatus.ESCALATED:
            # Check if the issue seems resolved
            last_msg = state.messages[-1] if state.messages else None
            if last_msg and last_msg.role == "agent":
                if any(word in last_msg.content.lower() 
                       for word in ['resolved', 'fixed', 'solved', 'all set']):
                    state.resolution_status = ResolutionStatus.SOLVED
    
    def get_customer_summary(self, email: str) -> Optional[Dict]:
        """Get summary of customer's conversation history."""
        if email not in self.conversations:
            return None
        
        state = self.conversations[email]
        return {
            "email": email,
            "name": state.customer_name,
            "total_messages": state.message_count,
            "channels_used": state.channels_used,
            "topics_discussed": state.topics_discussed,
            "current_sentiment": state.current_sentiment,
            "resolution_status": state.resolution_status.value,
            "is_escalated": state.resolution_status == ResolutionStatus.ESCALATED,
            "escalation_team": state.escalation_team
        }


class ProductDocsSearcher:
    """Simple keyword-based search over product documentation."""
    
    def __init__(self, docs_path: str):
        self.docs_path = docs_path
        self.content = self._load_docs()
        self.sections = self._parse_sections()
    
    def _load_docs(self) -> str:
        try:
            with open(self.docs_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""
    
    def _parse_sections(self) -> Dict[str, str]:
        """Parse docs into sections by heading."""
        sections = {}
        current_section = "intro"
        current_content = []
        
        for line in self.content.split('\n'):
            if line.startswith('## '):
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line.replace('## ', '').strip().lower()
                current_content = []
            else:
                current_content.append(line)
        
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def search(self, query: str) -> List[Tuple[str, str, float]]:
        """Search for relevant sections. Returns (section, excerpt, score)."""
        query_terms = query.lower().split()
        results = []
        
        for section, content in self.sections.items():
            content_lower = content.lower()
            score = sum(1 for term in query_terms if term in content_lower)
            
            if score > 0:
                excerpt = self._find_excerpt(content, query_terms)
                results.append((section, excerpt, score))
        
        return sorted(results, key=lambda x: x[2], reverse=True)[:3]
    
    def _find_excerpt(self, content: str, terms: List[str]) -> str:
        """Find a relevant excerpt containing search terms."""
        lines = content.split('\n')
        for line in lines:
            if any(term in line.lower() for term in terms):
                return line.strip()[:200]
        return content[:200].strip()


class EscalationDetector:
    """Detects when a message should be escalated to human support."""
    
    def __init__(self):
        self.pricing_keywords = [
            'discount', 'pricing', 'price', 'cost', 'cheaper', 'expensive',
            'budget', 'afford', 'negotiate', 'deal', 'quote', 'custom pricing',
            'enterprise pricing', 'upgrade cost', 'downgrade refund',
            'how much', 'charge', 'charges', 'charged', 'invoice', 'bill',
            'subscription cost', 'plan price', 'monthly', 'annual', 'yearly',
            'payment', 'pay', 'upgrade to', 'downgrade to', 'switch plan',
            'better deal', 'flexibility on pricing', 'best price', 'student discount'
        ]
        
        self.refund_keywords = [
            'refund', 'chargeback', 'money back', 'reverse charge',
            'cancel and refund', 'unauthorized charge', 'duplicate charge',
            'cancel my subscription', 'cancel subscription'
        ]
        
        self.legal_keywords = [
            'lawyer', 'attorney', 'lawsuit', 'sue', 'court', 'legal',
            'bbb', 'better business bureau', 'ftc', 'fraud', 'gdpr',
            'article 17', 'right to erasure', 'govern yourself'
        ]
        
        self.security_keywords = [
            'hacked', 'breach', 'unauthorized access', 'security',
            'compromised', 'strange login', 'unauthorized login',
            'former employee', 'data leak'
        ]
        
        self.human_request_keywords = [
            'talk to a human', 'real person', 'speak to someone',
            'human agent', 'not a bot', 'not a robot', 'actual person'
        ]
    
    def detect(self, message: str, sentiment: float = 0.5) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Detect if escalation is needed.
        Priority order: Legal > Security > Refund > Pricing > Human Request > Sentiment
        Returns: (needs_escalation, reason, team)
        """
        message_lower = message.lower()
        
        # CRITICAL: Check legal threats FIRST (highest priority)
        if any(kw in message_lower for kw in self.legal_keywords):
            return (True, "Legal/regulatory inquiry", "Legal Team")
        
        # CRITICAL: Check security concerns
        if any(kw in message_lower for kw in self.security_keywords):
            return (True, "Security concern", "Security Team")
        
        # HIGH: Check refund requests
        if any(kw in message_lower for kw in self.refund_keywords):
            return (True, "Refund request", "Billing Team")
        
        # MEDIUM: Check pricing (always escalate)
        if any(kw in message_lower for kw in self.pricing_keywords):
            return (True, "Pricing inquiry", "Sales Team")
        
        # MEDIUM: Check human request
        if any(kw in message_lower for kw in self.human_request_keywords):
            return (True, "Customer requested human", "Support Team")
        
        # MEDIUM-HIGH: Check low sentiment
        if sentiment < 0.3:
            return (True, f"Low sentiment score ({sentiment})", "Senior Support")
        
        return (False, None, None)


class ResponseFormatter:
    """Formats responses based on channel requirements."""
    
    WHATSAPP_MAX_CHARS = 300
    
    def format(self, response: str, channel: Channel, 
               customer_name: Optional[str] = None,
               is_followup: bool = False) -> str:
        """Format response for the specified channel."""
        if channel == Channel.EMAIL:
            return self._format_email(response, customer_name, is_followup)
        elif channel == Channel.WHATSAPP:
            return self._format_whatsapp(response)
        elif channel == Channel.WEB_FORM:
            return self._format_web_form(response, customer_name)
        return response
    
    def _format_email(self, response: str, customer_name: Optional[str] = None,
                      is_followup: bool = False) -> str:
        """Format for email with proper greeting and signature."""
        name = customer_name if customer_name else "there"
        
        # Different greeting for follow-up
        if is_followup:
            greeting = f"Hi again {name},"
        else:
            greeting = f"Dear {name},"
        
        return f"""{greeting}

Thank you for reaching out to TechCorp Support.

{response}

If you have any other questions, please don't hesitate to reach out.

Best regards,
TechCorp AI Support Team
support@techcorp.com"""
    
    def _format_whatsapp(self, response: str) -> str:
        """Format for WhatsApp - concise, under 300 characters."""
        if len(response) > self.WHATSAPP_MAX_CHARS:
            response = response[:self.WHATSAPP_MAX_CHARS - 3] + "..."
        return response
    
    def _format_web_form(self, response: str, customer_name: Optional[str] = None) -> str:
        """Format for web form - semi-formal, balanced."""
        greeting = f"Hello {customer_name}," if customer_name else "Hello,"
        return f"""{greeting}

Thanks for contacting TechCorp Support.

{response}

Feel free to reach out if you have any other questions.

Best,
TechCorp Support"""


class CustomerSuccessAgent:
    """
    Main agent with conversation memory and cross-channel identity.
    """
    
    def __init__(self, docs_path: str = "context/product-docs.md"):
        self.searcher = ProductDocsSearcher(docs_path)
        self.escalation_detector = EscalationDetector()
        self.formatter = ResponseFormatter()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.conversation_manager = ConversationManager()
    
    def process_message(self, message: CustomerMessage) -> AgentResponse:
        """Process a customer message with full conversation context."""
        # Ensure we have customer email (required for identity)
        if not message.customer_email:
            message.customer_email = "anonymous@example.com"
        
        # Get or create conversation state
        state = self.conversation_manager.get_or_create(message.customer_email)
        
        # Update customer name if provided
        if message.customer_name and not state.customer_name:
            state.customer_name = message.customer_name
        
        # Normalize message
        normalized = self._normalize_message(message)
        
        # Analyze sentiment
        sentiment = self.sentiment_analyzer.analyze(normalized)
        
        # Extract topics
        new_topics = self.conversation_manager.extract_topics(normalized)
        for topic in new_topics:
            if topic not in state.topics_discussed:
                state.topics_discussed.append(topic)
        
        # Get conversation context
        context = self.conversation_manager.get_context(state)
        is_followup = len(state.messages) > 0
        
        # Check for escalation (consider conversation history)
        needs_escalation, reason, team = self.escalation_detector.detect(
            normalized, 
            sentiment=sentiment
        )
        
        # Generate response
        if needs_escalation:
            response_text = self._generate_escalation_response(reason, team, context)
        else:
            response_text = self._generate_response(normalized, context, state)
        
        # Format for channel
        formatted_response = self.formatter.format(
            response_text, 
            message.channel,
            message.customer_name or state.customer_name,
            is_followup=is_followup
        )
        
        # Add customer message to history
        customer_msg = Message(
            role="customer",
            content=message.message,
            channel=message.channel,
            timestamp=message.timestamp or datetime.utcnow().isoformat(),
            subject=message.subject
        )
        self.conversation_manager.add_message(state, customer_msg)
        
        # Add agent response to history
        agent_msg = Message(
            role="agent",
            content=formatted_response,
            channel=message.channel,
            timestamp=datetime.utcnow().isoformat()
        )
        self.conversation_manager.add_message(state, agent_msg)
        
        # Update state
        self.conversation_manager.update_state(state, sentiment, needs_escalation, team)
        
        return AgentResponse(
            response=formatted_response,
            escalation_needed=needs_escalation,
            escalation_reason=reason,
            escalation_team=team,
            channel=message.channel,
            context_aware=bool(context),
            is_followup=is_followup
        )
    
    def get_customer_state(self, email: str) -> Optional[Dict]:
        """Get the current state of a customer's conversation."""
        return self.conversation_manager.get_customer_summary(email)
    
    def get_full_conversation(self, email: str) -> Optional[Dict]:
        """Get full conversation history for a customer."""
        if email not in self.conversation_manager.conversations:
            return None
        return self.conversation_manager.conversations[email].to_dict()
    
    def _normalize_message(self, message: CustomerMessage) -> str:
        """Normalize message content regardless of source."""
        parts = []
        if message.subject:
            parts.append(message.subject)
        parts.append(message.message)
        return ' '.join(parts)
    
    def _generate_response(self, query: str, context: str, 
                           state: ConversationState) -> str:
        """Generate a context-aware response."""
        # Check if this is a follow-up
        if context:
            # Look for follow-up indicators
            query_lower = query.lower()
            followup_indicators = ['yes', 'no', 'but', 'still', 'also', 'another', 
                                   'follow-up', 'update', 'more info', 'details']
            is_followup = any(ind in query_lower for ind in followup_indicators)
            
            if is_followup:
                return self._generate_contextual_response(query, context, state)
        
        # Standard response
        search_results = self.searcher.search(query)
        
        if not search_results:
            return """I wasn't able to find specific information about your question. 
Let me connect you with a team member who can provide more detailed assistance."""
        
        info_parts = []
        for section, excerpt, score in search_results:
            if excerpt and not excerpt.startswith('###'):
                info_parts.append(excerpt)
        
        if info_parts:
            return f"""Based on our documentation:

{' '.join(info_parts[:2])}

For more details, visit help.techcorp.com"""
        
        return """I found some relevant information. Let me know if you need more specific details!"""
    
    def _generate_contextual_response(self, query: str, context: str,
                                       state: ConversationState) -> str:
        """Generate a response that acknowledges conversation history."""
        # Get the original topic
        if state.topics_discussed:
            original_topic = state.topics_discussed[0]
            
            response = f"I see you're following up about {original_topic}. "
            
            # Add context-aware help
            if 'password' in query.lower() or 'reset' in query.lower():
                response += """To reset your password:
1. Go to techcorp.com/login
2. Click "Forgot Password?"
3. Enter your email address
4. Check your inbox for the reset link (valid for 1 hour)

Let me know if you need any other help with this!"""
            elif 'still' in query.lower() or 'not working' in query.lower():
                response += """I understand the issue persists. Let me escalate this to our technical team for deeper investigation. They'll reach out shortly."""
            else:
                response += """Based on our previous conversation, here's what I found:

For more details, you can also check help.techcorp.com"""
            
            return response
        
        return self._generate_response(query, "", state)
    
    def _generate_escalation_response(self, reason: str, team: str, 
                                       context: str) -> str:
        """Generate response when escalation is needed."""
        base = f"""I understand your concern. To ensure you get the best assistance, 
I'm connecting you with our {team} who specializes in this area.

They will respond within our standard response time for your plan tier."""
        
        if context:
            base += "\n\nI've included our conversation history for their reference."
        
        return base


def load_sample_tickets(path: str = "context/sample-tickets.json") -> List[Dict]:
    """Load sample tickets from JSON file."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('tickets', [])
    except FileNotFoundError:
        return []


def demo_cross_channel():
    """
    Demo: 3-message conversation across channels.
    Customer: sarah.johnson@acmecorp.com
    1. WhatsApp - Initial password reset question
    2. Email - Follow-up with more details
    3. Email - Agent response connecting both
    """
    print("=" * 70)
    print("TechCorp Customer Success AI Agent v2")
    print("Cross-Channel Conversation Demo")
    print("=" * 70)
    
    agent = CustomerSuccessAgent()
    
    customer_email = "sarah.johnson@acmecorp.com"
    
    # Message 1: WhatsApp - Initial question
    print("\n" + "=" * 70)
    print("MESSAGE 1 - WhatsApp (Initial)")
    print("=" * 70)
    
    msg1 = CustomerMessage(
        channel=Channel.WHATSAPP,
        message="hey i forgot my password and cant login. how do i reset it?",
        customer_email=customer_email,
        customer_name="Sarah Johnson",
        timestamp="2025-01-20T10:15:00Z"
    )
    
    print(f"\n📩 Customer ({msg1.channel.value}): {msg1.message}")
    
    response1 = agent.process_message(msg1)
    
    print(f"\n🤖 Agent Response ({len(response1.response)} chars):")
    print(response1.response)
    print(f"\n📊 Context Aware: {response1.context_aware} | Follow-up: {response1.is_followup}")
    
    # Message 2: Email - Follow-up with details
    print("\n" + "=" * 70)
    print("MESSAGE 2 - Email (Follow-up from same customer)")
    print("=" * 70)
    
    msg2 = CustomerMessage(
        channel=Channel.EMAIL,
        message="Thanks for the info. I tried the reset link but it's showing 'link expired'. I clicked it about 2 hours after receiving it. Can you help me get a new link or reset it manually? My account email is sarah.johnson@acmecorp.com",
        subject="Re: Password Reset - Link Expired",
        customer_email=customer_email,
        timestamp="2025-01-20T10:45:00Z"
    )
    
    print(f"\n📩 Customer ({msg2.channel.value}):")
    print(f"   Subject: {msg2.subject}")
    print(f"   Message: {msg2.message[:150]}...")
    
    response2 = agent.process_message(msg2)
    
    print(f"\n🤖 Agent Response ({len(response2.response)} chars):")
    print(response2.response)
    print(f"\n📊 Context Aware: {response2.context_aware} | Follow-up: {response2.is_followup}")
    
    # Show final state
    print("\n" + "=" * 70)
    print("FINAL CONVERSATION STATE")
    print("=" * 70)
    
    state = agent.get_full_conversation(customer_email)
    
    if state:
        print(f"""
Customer: {state['customer_name']} ({state['customer_email']})
Conversation Started: {state['created_at']}
Last Updated: {state['updated_at']}

--- Channel History ---
Original Channel: {state['original_channel']}
Channels Used: {state.get('channels_used', state.get('channel_switches', []))}
Channel Switches: {state['channel_switches']}

--- Conversation Stats ---
Total Messages: {state['total_messages']}
Topics Discussed: {state['topics_discussed']}
Sentiment History: {state['sentiment_history']}
Current Sentiment: {state['current_sentiment']:.2f}

--- Resolution Status ---
Status: {state['resolution_status']}
Escalated: {state['is_escalated']}
Escalation Team: {state['escalation_team']}

--- Message History ---
""")
        
        for i, msg in enumerate(state['messages'], 1):
            print(f"{i}. [{msg['channel']}] {msg['role'].upper()}:")
            if msg['subject']:
                print(f"   Subject: {msg['subject']}")
            print(f"   Content: {msg['content'][:100]}...")
            print()
    
    # Show customer summary
    print("\n" + "=" * 70)
    print("CUSTOMER SUMMARY (Cross-Channel Identity)")
    print("=" * 70)
    
    summary = agent.get_customer_state(customer_email)
    if summary:
        print(f"""
Email: {summary['email']}
Name: {summary['name']}
Total Messages: {summary['total_messages']}
Channels Used: {summary['channels_used']}
Topics Discussed: {summary['topics_discussed']}
Current Sentiment: {summary['current_sentiment']:.2f}
Resolution Status: {summary['resolution_status']}
Is Escalated: {summary['is_escalated']}
""")
    
    print("=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✓ Conversation memory across messages")
    print("  ✓ Cross-channel identity (WhatsApp → Email)")
    print("  ✓ Context-aware follow-up responses")
    print("  ✓ State tracking (sentiment, topics, channels)")
    print("  ✓ Full conversation history preserved")
    print("=" * 70)


if __name__ == "__main__":
    demo_cross_channel()
