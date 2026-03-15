"""
TechCorp Customer Success AI Agent - Sentiment Analysis Middleware

This module implements sentiment-based routing for incoming customer messages.
It analyzes sentiment and automatically flags 'Angry' or 'Urgent' tickets for
human escalation in the PostgreSQL DB.

SENTIMENT ANALYSIS IMPLEMENTATION:
----------------------------------
- Uses Hugging Face transformers for accurate sentiment analysis
- Supports multiple models (distilbert, roberta, bert)
- Caches model results for performance
- Integrates with Kafka message processing
- Auto-escalates based on sentiment thresholds

ESCALATION THRESHOLDS:
---------------------
- Sentiment < 0.3: Auto-escalate to Senior Support
- Sentiment < 0.2: Mark as 'Urgent' + escalate
- Sentiment < 0.1: Mark as 'Critical' + immediate escalation
- Angry keywords detected: Override sentiment score to 0.2

Author: AI Engineering Team
Version: 1.0.0
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import transformers, fallback to keyword-based if not available
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers not available. Falling back to keyword-based sentiment analysis.")

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS AND MODELS
# ============================================================================

class SentimentLabel(str, Enum):
    """Sentiment label categories."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class EscalationUrgency(str, Enum):
    """Escalation urgency levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SentimentResult:
    """Result of sentiment analysis."""
    sentiment_score: float  # 0.0 to 1.0
    sentiment_label: SentimentLabel
    confidence: float  # 0.0 to 1.0
    emotional_indicators: List[str]
    escalation_recommended: bool
    urgency_level: EscalationUrgency
    model_used: str
    processing_time_ms: float


@dataclass
class EscalationDecision:
    """Decision for escalation based on sentiment."""
    should_escalate: bool
    reason: str
    urgency: EscalationUrgency
    assigned_team: str
    trigger_keywords: List[str]
    sentiment_score: float


# ============================================================================
# ANGER KEYWORD DETECTION
# ============================================================================

ANGER_KEYWORDS = {
    'extreme_anger': [
        'fucking', 'fucking ridiculous', 'absolutely unacceptable',
        'worst service ever', 'completely useless', 'waste of money',
        'goddamn', 'shit', 'damn this', 'horrible', 'disgusting',
        'are you kidding me', 'you have got to be kidding', 'unbelievable'
    ],
    'threats': [
        'cancel my account', 'switching to competitor', 'going elsewhere',
        'never using again', 'done with this', 'fed up', 'had enough'
    ],
    'frustration': [
        'third time', 'fourth time', 'fifth time', 'again and again',
        'still not working', 'keeps happening', 'every single time',
        'no one listens', 'nobody cares', 'ignoring me'
    ],
    'urgency': [
        'immediately', 'right now', 'asap', 'urgent', 'emergency',
        'critical', 'broken', 'down', 'not working at all'
    ]
}

# Escalation team mapping
ESCALATION_TEAMS = {
    'very_negative': 'Senior Support',
    'negative': 'Support Team',
    'extreme_anger': 'Senior Support',
    'threats': 'Retention Team',
    'frustration': 'Senior Support',
    'urgency': 'Support Team'
}


# ============================================================================
# SENTIMENT ANALYZER CLASS
# ============================================================================

class SentimentAnalyzer:
    """
    Sentiment analysis for customer messages.
    
    Uses Hugging Face transformers when available, falls back to
    keyword-based analysis otherwise.
    """
    
    def __init__(self, model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"):
        self.model_name = model_name
        self.pipeline = None
        self.tokenizer = None
        self.model = None
        
        if TRANSFORMERS_AVAILABLE:
            self._load_model()
        else:
            logger.warning("Using keyword-based sentiment analysis (fallback)")
    
    def _load_model(self):
        """Load the sentiment analysis model."""
        try:
            logger.info(f"Loading sentiment model: {self.model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            
            self.pipeline = pipeline(
                "sentiment-analysis",
                model=self.model,
                tokenizer=self.tokenizer,
                return_all_scores=False,
                truncation=True,
                max_length=512
            )
            
            logger.info(f"✓ Sentiment model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load sentiment model: {e}")
            logger.warning("Falling back to keyword-based analysis")
    
    def analyze(self, text: str) -> SentimentResult:
        """
        Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            SentimentResult with score, label, and metadata
        """
        import time
        start_time = time.time()
        
        if TRANSFORMERS_AVAILABLE and self.pipeline:
            result = self._analyze_with_transformers(text)
        else:
            result = self._analyze_with_keywords(text)
        
        # Calculate processing time
        result.processing_time_ms = (time.time() - start_time) * 1000
        
        # Detect anger keywords
        anger_indicators = self._detect_anger_keywords(text)
        if anger_indicators:
            result.emotional_indicators.extend(anger_indicators)
            
            # Override sentiment if extreme anger detected
            if 'extreme_anger' in anger_indicators or 'threats' in anger_indicators:
                if result.sentiment_score > 0.2:
                    result.sentiment_score = 0.2
                    result.sentiment_label = SentimentLabel.NEGATIVE
                result.escalation_recommended = True
        
        # Determine urgency level
        result.urgency_level = self._determine_urgency(result)
        
        return result
    
    def _analyze_with_transformers(self, text: str) -> SentimentResult:
        """Analyze using Hugging Face transformers."""
        try:
            # Run inference
            result = self.pipeline(text[:512])[0]  # Truncate to max length
            
            # Extract score
            label = result['label']
            score = result['score']
            
            # Convert to 0-1 scale (higher = more positive)
            if label == 'POSITIVE':
                sentiment_score = score
            else:  # NEGATIVE
                sentiment_score = 1.0 - score
            
            # Determine label
            if sentiment_score >= 0.7:
                sentiment_label = SentimentLabel.POSITIVE
            elif sentiment_score >= 0.4:
                sentiment_label = SentimentLabel.NEUTRAL
            elif sentiment_score >= 0.3:
                sentiment_label = SentimentLabel.NEGATIVE
            else:
                sentiment_label = SentimentLabel.VERY_NEGATIVE
            
            return SentimentResult(
                sentiment_score=sentiment_score,
                sentiment_label=sentiment_label,
                confidence=score,
                emotional_indicators=[],
                escalation_recommended=sentiment_score < 0.3,
                urgency_level=EscalationUrgency.LOW,  # Will be updated
                model_used=self.model_name,
                processing_time_ms=0
            )
            
        except Exception as e:
            logger.error(f"Transformer inference failed: {e}")
            return self._analyze_with_keywords(text)
    
    def _analyze_with_keywords(self, text: str) -> SentimentResult:
        """
        Fallback keyword-based sentiment analysis.
        
        Uses positive/negative word lists and intensity modifiers.
        """
        text_lower = text.lower()
        
        # Positive words
        positive_words = [
            'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'love', 'loving', 'happy', 'pleased', 'satisfied',
            'thank', 'thanks', 'appreciate', 'helpful', 'awesome',
            'perfect', 'best', 'good', 'nice', 'brilliant'
        ]
        
        # Negative words
        negative_words = [
            'terrible', 'awful', 'horrible', 'worst', 'hate',
            'angry', 'frustrated', 'disappointed', 'upset', 'annoyed',
            'useless', 'broken', 'failed', 'failure', 'problem',
            'issue', 'wrong', 'bad', 'poor', 'disappointing'
        ]
        
        # Count occurrences
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        # Calculate score
        total = positive_count + negative_count
        if total == 0:
            sentiment_score = 0.5  # Neutral
            sentiment_label = SentimentLabel.NEUTRAL
        else:
            # Score: 0.0 (all negative) to 1.0 (all positive)
            sentiment_score = positive_count / total
            sentiment_label = SentimentLabel.NEUTRAL
            
            if sentiment_score >= 0.7:
                sentiment_label = SentimentLabel.POSITIVE
            elif sentiment_score >= 0.4:
                sentiment_label = SentimentLabel.NEUTRAL
            elif sentiment_score >= 0.3:
                sentiment_label = SentimentLabel.NEGATIVE
            else:
                sentiment_label = SentimentLabel.VERY_NEGATIVE
        
        # Confidence based on word count
        confidence = min(0.5 + (total * 0.1), 0.95)
        
        # Emotional indicators
        emotional_indicators = []
        for word in positive_words + negative_words:
            if word in text_lower:
                emotional_indicators.append(word)
        
        return SentimentResult(
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
            confidence=confidence,
            emotional_indicators=emotional_indicators,
            escalation_recommended=sentiment_score < 0.3,
            urgency_level=EscalationUrgency.LOW,
            model_used="keyword_based",
            processing_time_ms=0
        )
    
    def _detect_anger_keywords(self, text: str) -> List[str]:
        """Detect anger-related keywords in text."""
        text_lower = text.lower()
        detected = []
        
        for category, keywords in ANGER_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                detected.append(category)
        
        return detected
    
    def _determine_urgency(self, result: SentimentResult) -> EscalationUrgency:
        """Determine escalation urgency based on sentiment."""
        if result.sentiment_score < 0.1:
            return EscalationUrgency.CRITICAL
        elif result.sentiment_score < 0.2:
            return EscalationUrgency.HIGH
        elif result.sentiment_score < 0.3:
            return EscalationUrgency.MEDIUM
        elif result.sentiment_score < 0.5:
            return EscalationUrgency.LOW
        else:
            return EscalationUrgency.LOW


# ============================================================================
# SENTIMENT-BASED ROUTING MIDDLEWARE
# ============================================================================

class SentimentRoutingMiddleware:
    """
    Middleware for sentiment-based message routing.
    
    Intercepts incoming messages, analyzes sentiment, and routes
    to appropriate escalation queue if needed.
    """
    
    def __init__(self, analyzer: Optional[SentimentAnalyzer] = None):
        self.analyzer = analyzer or SentimentAnalyzer()
        self.escalation_threshold = 0.3
        self.urgent_threshold = 0.2
        self.critical_threshold = 0.1
    
    async def process_message(
        self,
        message: str,
        customer_id: str,
        ticket_id: Optional[str] = None
    ) -> Tuple[SentimentResult, Optional[EscalationDecision]]:
        """
        Process a message through sentiment analysis and routing.
        
        Args:
            message: Customer message text
            customer_id: Customer identifier
            ticket_id: Optional ticket ID
            
        Returns:
            Tuple of (SentimentResult, Optional[EscalationDecision])
        """
        # Analyze sentiment
        sentiment_result = self.analyzer.analyze(message)
        
        logger.info(
            f"Sentiment Analysis: score={sentiment_result.sentiment_score:.3f}, "
            f"label={sentiment_result.sentiment_label.value}, "
            f"escalation={sentiment_result.escalation_recommended}"
        )
        
        # Determine if escalation needed
        escalation_decision = None
        if sentiment_result.escalation_recommended:
            escalation_decision = self._create_escalation_decision(
                sentiment_result,
                customer_id,
                ticket_id
            )
            
            logger.info(
                f"Escalation Decision: urgency={escalation_decision.urgency.value}, "
                f"team={escalation_decision.assigned_team}, "
                f"reason={escalation_decision.reason}"
            )
        
        return sentiment_result, escalation_decision
    
    def _create_escalation_decision(
        self,
        sentiment: SentimentResult,
        customer_id: str,
        ticket_id: Optional[str]
    ) -> EscalationDecision:
        """Create escalation decision based on sentiment."""
        # Determine reason
        if sentiment.sentiment_score < self.critical_threshold:
            reason = f"Critical sentiment score: {sentiment.sentiment_score:.3f}"
            urgency = EscalationUrgency.CRITICAL
            team = 'Senior Support'
        elif sentiment.sentiment_score < self.urgent_threshold:
            reason = f"Urgent: Very negative sentiment ({sentiment.sentiment_score:.3f})"
            urgency = EscalationUrgency.HIGH
            team = 'Senior Support'
        elif sentiment.sentiment_score < self.escalation_threshold:
            reason = f"Negative sentiment detected ({sentiment.sentiment_score:.3f})"
            urgency = EscalationUrgency.MEDIUM
            team = 'Support Team'
        else:
            reason = "Sentiment-based escalation"
            urgency = EscalationUrgency.LOW
            team = 'Support Team'
        
        # Add specific triggers
        trigger_keywords = sentiment.emotional_indicators[:5]  # Top 5 indicators
        
        return EscalationDecision(
            should_escalate=True,
            reason=reason,
            urgency=urgency,
            assigned_team=team,
            trigger_keywords=trigger_keywords,
            sentiment_score=sentiment.sentiment_score
        )
    
    def flag_ticket_for_escalation(
        self,
        ticket_id: str,
        escalation: EscalationDecision,
        sentiment: SentimentResult
    ) -> Dict[str, Any]:
        """
        Flag a ticket for escalation in the database.
        
        Args:
            ticket_id: Ticket to flag
            escalation: Escalation decision
            sentiment: Sentiment analysis result
            
        Returns:
            Database update payload
        """
        return {
            "ticket_id": ticket_id,
            "updates": {
                "priority": self._map_urgency_to_priority(escalation.urgency),
                "status": "escalated",
                "escalation_reason": escalation.reason,
                "assigned_team": escalation.assigned_team,
                "sentiment_score": sentiment.sentiment_score,
                "sentiment_label": sentiment.sentiment_label.value,
                "requires_human_review": True,
                "escalation_triggered_at": datetime.utcnow().isoformat()
            },
            "metadata": {
                "trigger_type": "sentiment_analysis",
                "model_used": sentiment.model_used,
                "processing_time_ms": sentiment.processing_time_ms,
                "emotional_indicators": sentiment.emotional_indicators,
                "trigger_keywords": escalation.trigger_keywords
            }
        }
    
    def _map_urgency_to_priority(self, urgency: EscalationUrgency) -> str:
        """Map urgency level to ticket priority."""
        mapping = {
            EscalationUrgency.CRITICAL: "critical",
            EscalationUrgency.HIGH: "high",
            EscalationUrgency.MEDIUM: "high",
            EscalationUrgency.LOW: "medium"
        }
        return mapping.get(urgency, "medium")


# ============================================================================
# KAFKA INTEGRATION
# ============================================================================

class SentimentKafkaProcessor:
    """
    Kafka processor for sentiment-based routing.
    
    Listens to incoming messages, analyzes sentiment, and publishes
    escalation events when needed.
    """
    
    def __init__(self, middleware: SentimentRoutingMiddleware):
        self.middleware = middleware
        self.kafka_producer = None
        self.running = False
    
    async def start(self):
        """Start the Kafka processor."""
        logger.info("Starting Sentiment Kafka Processor...")
        self.running = True
        
        # Import aiokafka
        try:
            from aiokafka import AIOKafkaProducer
            self.kafka_producer = AIOKafkaProducer(
                bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            await self.kafka_producer.start()
            logger.info("✓ Kafka producer started")
        except Exception as e:
            logger.error(f"Failed to start Kafka producer: {e}")
            logger.warning("Running without Kafka - escalations will be logged only")
    
    async def stop(self):
        """Stop the Kafka processor."""
        self.running = False
        if self.kafka_producer:
            await self.kafka_producer.stop()
            logger.info("Kafka producer stopped")
    
    async def process_incoming_message(
        self,
        message: str,
        customer_id: str,
        ticket_id: str,
        channel: str
    ):
        """
        Process an incoming message from Kafka.
        
        Args:
            message: Customer message text
            customer_id: Customer identifier
            ticket_id: Ticket ID
            channel: Communication channel
        """
        try:
            # Analyze sentiment and get escalation decision
            sentiment, escalation = await self.middleware.process_message(
                message=message,
                customer_id=customer_id,
                ticket_id=ticket_id
            )
            
            # If escalation needed, publish to escalation topic
            if escalation:
                escalation_event = self.middleware.flag_ticket_for_escalation(
                    ticket_id=ticket_id,
                    escalation=escalation,
                    sentiment=sentiment
                )
                
                await self._publish_escalation(escalation_event, channel)
            
            # Publish sentiment metrics
            await self._publish_sentiment_metrics(
                ticket_id=ticket_id,
                sentiment=sentiment,
                channel=channel
            )
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def _publish_escalation(self, escalation_event: Dict, channel: str):
        """Publish escalation event to Kafka."""
        if not self.kafka_producer:
            logger.warning(f"Escalation (not published): {escalation_event['ticket_id']}")
            return
        
        try:
            topic = "fte.escalations"
            
            message = {
                "event_type": "sentiment_escalation",
                "timestamp": datetime.utcnow().isoformat(),
                "channel": channel,
                **escalation_event
            }
            
            await self.kafka_producer.send_and_wait(
                topic=topic,
                value=message,
                key=escalation_event['ticket_id'].encode('utf-8')
            )
            
            logger.info(f"✓ Escalation published to {topic}: {escalation_event['ticket_id']}")
            
        except Exception as e:
            logger.error(f"Failed to publish escalation: {e}")
    
    async def _publish_sentiment_metrics(self, ticket_id: str, sentiment: SentimentResult, channel: str):
        """Publish sentiment metrics to Kafka."""
        if not self.kafka_producer:
            return
        
        try:
            topic = "fte.metrics.sentiment"
            
            metrics = {
                "ticket_id": ticket_id,
                "channel": channel,
                "sentiment_score": sentiment.sentiment_score,
                "sentiment_label": sentiment.sentiment_label.value,
                "confidence": sentiment.confidence,
                "model_used": sentiment.model_used,
                "processing_time_ms": sentiment.processing_time_ms,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.kafka_producer.send_and_wait(
                topic=topic,
                value=metrics
            )
            
        except Exception as e:
            logger.error(f"Failed to publish sentiment metrics: {e}")


# ============================================================================
# FASTAPI MIDDLEWARE
# ============================================================================

def create_sentiment_middleware_app():
    """
    Create a FastAPI app for sentiment analysis as a service.
    
    This can be run as a standalone microservice or integrated
    into the main API.
    """
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware import Middleware
    
    app = FastAPI(title="Sentiment Analysis Service")
    middleware = SentimentRoutingMiddleware()
    
    @app.post("/analyze", response_model=Dict[str, Any])
    async def analyze_sentiment(text: str, customer_id: str):
        """Analyze sentiment of text."""
        try:
            result = middleware.analyzer.analyze(text)
            
            return {
                "success": True,
                "sentiment_score": result.sentiment_score,
                "sentiment_label": result.sentiment_label.value,
                "confidence": result.confidence,
                "emotional_indicators": result.emotional_indicators,
                "escalation_recommended": result.escalation_recommended,
                "urgency_level": result.urgency_level.value,
                "model_used": result.model_used,
                "processing_time_ms": result.processing_time_ms
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/route", response_model=Dict[str, Any])
    async def route_message(text: str, customer_id: str, ticket_id: str):
        """Analyze and route message based on sentiment."""
        try:
            sentiment, escalation = await middleware.process_message(
                message=text,
                customer_id=customer_id,
                ticket_id=ticket_id
            )
            
            response = {
                "success": True,
                "sentiment": {
                    "score": sentiment.sentiment_score,
                    "label": sentiment.sentiment_label.value,
                    "confidence": sentiment.confidence
                },
                "escalation": None
            }
            
            if escalation:
                response["escalation"] = {
                    "should_escalate": escalation.should_escalate,
                    "reason": escalation.reason,
                    "urgency": escalation.urgency.value,
                    "assigned_team": escalation.assigned_team,
                    "trigger_keywords": escalation.trigger_keywords
                }
            
            return response
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return app


# ============================================================================
# MAIN / TESTING
# ============================================================================

async def test_sentiment_analyzer():
    """Test the sentiment analyzer with sample messages."""
    analyzer = SentimentAnalyzer()
    middleware = SentimentRoutingMiddleware(analyzer)
    
    test_messages = [
        ("I love your product! It's amazing!", "happy_customer"),
        ("This is absolutely unacceptable! I want a refund NOW!", "angry_customer"),
        ("The app keeps crashing every 5 minutes. This is so frustrating.", "frustrated_customer"),
        ("I need help with my password reset please.", "neutral_customer"),
        ("WHY DOES THIS APP KEEP LOGGING ME OUT??? SO ANNOYING!!!", "very_angry_customer"),
        ("Thank you so much for the quick help. Great support!", "grateful_customer"),
    ]
    
    print("=" * 70)
    print("Sentiment Analyzer Test Results")
    print("=" * 70)
    
    for message, customer_id in test_messages:
        print(f"\nCustomer: {customer_id}")
        print(f"Message: {message}")
        print("-" * 70)
        
        result = analyzer.analyze(message)
        
        print(f"Score: {result.sentiment_score:.3f}")
        print(f"Label: {result.sentiment_label.value}")
        print(f"Confidence: {result.confidence:.3f}")
        print(f"Escalation Recommended: {result.escalation_recommended}")
        print(f"Urgency: {result.urgency_level.value}")
        print(f"Emotional Indicators: {result.emotional_indicators[:5]}")
        print(f"Processing Time: {result.processing_time_ms:.2f}ms")
        
        # Test routing
        _, escalation = await middleware.process_message(message, customer_id, "tkt_test")
        if escalation:
            print(f"\n🚨 ESCALATION:")
            print(f"   Reason: {escalation.reason}")
            print(f"   Urgency: {escalation.urgency.value}")
            print(f"   Team: {escalation.assigned_team}")
    
    print("\n" + "=" * 70)
    print("Test Complete")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_sentiment_analyzer())
