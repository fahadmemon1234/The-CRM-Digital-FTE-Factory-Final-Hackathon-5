"""
TechCorp Customer Success AI Agent - Sentiment-Driven Kafka Producer

FastAPI webhook handlers that analyze sentiment of incoming messages and route
to appropriate Kafka topics based on sentiment analysis.

HACKATHON 5 SPECIALIZATION CRITERIA:
------------------------------------
✅ Sentiment Analysis: Analyze incoming message sentiment
✅ Kafka Routing: 'Angry' messages → fte.tickets.urgent topic
✅ FastAPI Webhooks: Gmail, WhatsApp, Web Form handlers
✅ Async-First: Fully async/await pattern
✅ Production-Ready: Error handling, retries, circuit breaker

Author: AI Engineering Team
Version: 1.0.0 (Production)
Hackathon: CRM Digital FTE Factory Hackathon 5 - Specialization Track
"""

import asyncio
import logging
import os
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager

# FastAPI
from fastapi import FastAPI, HTTPException, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator

# Kafka
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.errors import KafkaError, KafkaTimeoutError

# Sentiment Analysis
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch

logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class KafkaConfig:
    """Kafka configuration."""
    bootstrap_servers: str = field(default_factory=lambda: os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'))
    
    # Topics
    topic_tickets_incoming: str = "fte.tickets.incoming"
    topic_tickets_urgent: str = "fte.tickets.urgent"
    topic_sentiment_metrics: str = "fte.metrics.sentiment"
    topic_escalations: str = "fte.escalations"
    
    # Producer settings
    producer_acks: str = "all"  # Wait for all replicas
    producer_retries: int = 3
    producer_retry_backoff_ms: int = 100
    producer_timeout_ms: int = 30000
    
    # Consumer settings
    consumer_group_id: str = "fte-sentiment-processor"
    consumer_auto_offset_reset: str = "earliest"
    
    # Circuit breaker
    circuit_failure_threshold: int = 5
    circuit_reset_timeout_seconds: int = 60


@dataclass
class SentimentConfig:
    """Sentiment analysis configuration."""
    model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"
    
    # Sentiment thresholds
    angry_threshold: float = 0.3  # Score below this = angry
    urgent_threshold: float = 0.2  # Score below this = very urgent
    critical_threshold: float = 0.1  # Score below this = critical
    
    # Anger keywords (override sentiment score)
    anger_keywords: List[str] = field(default_factory=lambda: [
        'fucking', 'ridiculous', 'unacceptable', 'worst', 'hate',
        'angry', 'frustrated', 'disappointed', 'upset', 'annoyed',
        'useless', 'broken', 'failed', 'terrible', 'awful',
        'cancel', 'lawsuit', 'legal', 'refund', 'chargeback'
    ])
    
    # Processing
    max_text_length: int = 512
    batch_size: int = 1


# Global configuration
KAFKA_CONFIG = KafkaConfig()
SENTIMENT_CONFIG = SentimentConfig()


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class SentimentLabel(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"
    ANGRY = "angry"


class ChannelType(str, Enum):
    GMAIL = "gmail"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Gmail webhook models
class GmailMessage(BaseModel):
    message_id: str
    thread_id: str
    from_email: str
    from_name: Optional[str] = None
    to: str
    subject: Optional[str] = None
    body: str
    received_at: datetime
    labels: List[str] = field(default_factory=list)


# WhatsApp webhook models
class WhatsAppMessage(BaseModel):
    message_sid: str
    from_number: str
    to_number: str
    body: str
    timestamp: datetime
    media_url: Optional[str] = None


# Web form models
class WebFormSubmission(BaseModel):
    submission_id: str
    name: str
    email: str
    phone: Optional[str] = None
    subject: str
    category: str
    message: str
    priority: Optional[TicketPriority] = TicketPriority.MEDIUM
    submitted_at: datetime = field(default_factory=datetime.utcnow)


# Sentiment analysis result
class SentimentResult(BaseModel):
    score: float  # 0.0 to 1.0 (higher = more positive)
    label: SentimentLabel
    confidence: float
    emotional_indicators: List[str] = field(default_factory=list)
    is_angry: bool
    urgency_level: str
    processing_time_ms: float


# Kafka message envelope
class KafkaMessage(BaseModel):
    event_type: str
    timestamp: datetime
    channel: str
    message_id: str
    customer_id: str
    payload: Dict[str, Any]
    sentiment: Optional[SentimentResult] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# CIRCUIT BREAKER
# ============================================================================

class CircuitBreaker:
    """
    Circuit breaker for Kafka producer.
    
    Prevents cascading failures when Kafka is unavailable.
    """
    
    def __init__(self, failure_threshold: int = 5, reset_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half-open
    
    def record_success(self):
        """Record successful operation."""
        self.failures = 0
        self.state = "closed"
    
    def record_failure(self):
        """Record failed operation."""
        self.failures += 1
        self.last_failure_time = time.time()
        
        if self.failures >= self.failure_threshold:
            self.state = "open"
            logger.warning(f"Circuit breaker opened after {self.failures} failures")
    
    def can_execute(self) -> bool:
        """Check if operation can be executed."""
        if self.state == "closed":
            return True
        
        if self.state == "open":
            # Check if reset timeout has passed
            if self.last_failure_time and (time.time() - self.last_failure_time) > self.reset_timeout:
                self.state = "half-open"
                logger.info("Circuit breaker entering half-open state")
                return True
            return False
        
        # half-open state - allow one test
        return True


# ============================================================================
# SENTIMENT ANALYZER
# ============================================================================

class SentimentAnalyzer:
    """
    Production sentiment analyzer using Hugging Face transformers.
    """
    
    def __init__(self, config: SentimentConfig):
        self.config = config
        self.pipeline = None
        self.tokenizer = None
        self.model = None
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"Initializing sentiment analyzer on {self._device}")
        self._load_model()
    
    def _load_model(self):
        """Load sentiment analysis model."""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.config.model_name)
            
            if self._device == "cuda":
                self.model.to("cuda")
            
            self.pipeline = pipeline(
                "sentiment-analysis",
                model=self.model,
                tokenizer=self.tokenizer,
                return_all_scores=False,
                truncation=True,
                max_length=self.config.max_text_length,
                device=0 if self._device == "cuda" else -1
            )
            
            logger.info(f"✓ Sentiment model loaded: {self.config.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to load sentiment model: {e}")
            raise
    
    def analyze(self, text: str) -> SentimentResult:
        """
        Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            SentimentResult with score and label
        """
        start_time = time.time()
        
        # Detect anger keywords
        text_lower = text.lower()
        anger_indicators = [
            keyword for keyword in self.config.anger_keywords
            if keyword in text_lower
        ]
        
        # Run model inference
        try:
            result = self.pipeline(text[:self.config.max_text_length])[0]
            
            label = result['label']
            score = result['score']
            
            # Convert to 0-1 scale (higher = more positive)
            if label == 'POSITIVE':
                sentiment_score = score
            else:
                sentiment_score = 1.0 - score
            
        except Exception as e:
            logger.error(f"Sentiment inference failed: {e}")
            sentiment_score = 0.5  # Default to neutral
        
        # Override if anger keywords detected
        if anger_indicators and sentiment_score > 0.3:
            sentiment_score = 0.25  # Override to negative
        
        # Determine label
        if sentiment_score < self.config.critical_threshold:
            sentiment_label = SentimentLabel.VERY_NEGATIVE
        elif sentiment_score < self.config.urgent_threshold:
            sentiment_label = SentimentLabel.ANGRY
        elif sentiment_score < self.config.angry_threshold:
            sentiment_label = SentimentLabel.NEGATIVE
        elif sentiment_score < 0.5:
            sentiment_label = SentimentLabel.NEUTRAL
        else:
            sentiment_label = SentimentLabel.POSITIVE
        
        # Determine urgency
        if sentiment_score < self.config.critical_threshold:
            urgency_level = "critical"
        elif sentiment_score < self.config.urgent_threshold:
            urgency_level = "urgent"
        elif sentiment_score < self.config.angry_threshold:
            urgency_level = "high"
        else:
            urgency_level = "normal"
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        return SentimentResult(
            score=sentiment_score,
            label=sentiment_label,
            confidence=score if label == 'POSITIVE' else 1.0 - score,
            emotional_indicators=anger_indicators,
            is_angry=sentiment_score < self.config.angry_threshold or len(anger_indicators) > 0,
            urgency_level=urgency_level,
            processing_time_ms=processing_time_ms
        )


# ============================================================================
# KAFKA PRODUCER MANAGER
# ============================================================================

class KafkaProducerManager:
    """
    Manages Kafka producer with circuit breaker and retry logic.
    """
    
    def __init__(self, config: KafkaConfig):
        self.config = config
        self.producer: Optional[AIOKafkaProducer] = None
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=config.circuit_failure_threshold,
            reset_timeout=config.circuit_reset_timeout_seconds
        )
        self._metrics = {
            "messages_sent": 0,
            "messages_failed": 0,
            "urgent_messages": 0,
            "avg_latency_ms": 0.0
        }
    
    async def start(self):
        """Start Kafka producer."""
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.config.bootstrap_servers,
                acks=self.config.producer_acks,
                retries=self.config.producer_retries,
                retry_backoff_ms=self.config.producer_retry_backoff_ms,
                request_timeout_ms=self.config.producer_timeout_ms,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
            
            await self.producer.start()
            logger.info("✓ Kafka producer started")
            
        except Exception as e:
            logger.error(f"Failed to start Kafka producer: {e}")
            raise
    
    async def stop(self):
        """Stop Kafka producer."""
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped")
    
    async def send(
        self,
        topic: str,
        value: Dict[str, Any],
        key: Optional[str] = None,
        max_retries: int = 3
    ):
        """
        Send message to Kafka topic with retry logic.
        
        Args:
            topic: Kafka topic
            value: Message value
            key: Message key (for partitioning)
            max_retries: Maximum retry attempts
        """
        # Check circuit breaker
        if not self.circuit_breaker.can_execute():
            logger.warning(f"Circuit breaker open - dropping message to {topic}")
            self._metrics["messages_failed"] += 1
            return
        
        start_time = time.time()
        
        for attempt in range(max_retries):
            try:
                if not self.producer:
                    raise RuntimeError("Kafka producer not started")
                
                await self.producer.send_and_wait(
                    topic=topic,
                    value=value,
                    key=key
                )
                
                # Record success
                self.circuit_breaker.record_success()
                self._metrics["messages_sent"] += 1
                
                if topic == self.config.topic_tickets_urgent:
                    self._metrics["urgent_messages"] += 1
                
                # Update latency
                latency_ms = (time.time() - start_time) * 1000
                self._metrics["avg_latency_ms"] = (
                    (self._metrics["avg_latency_ms"] * (self._metrics["messages_sent"] - 1) + latency_ms)
                    / self._metrics["messages_sent"]
                )
                
                logger.debug(f"✓ Message sent to {topic} (latency: {latency_ms:.2f}ms)")
                return
                
            except (KafkaError, KafkaTimeoutError) as e:
                logger.warning(f"Kafka send attempt {attempt + 1} failed: {e}")
                
                if attempt == max_retries - 1:
                    self.circuit_breaker.record_failure()
                    self._metrics["messages_failed"] += 1
                    logger.error(f"Failed to send message after {max_retries} attempts")
                    raise
                
                # Wait before retry
                await asyncio.sleep(self.config.producer_retry_backoff_ms * (attempt + 1) / 1000)
                
            except Exception as e:
                logger.error(f"Unexpected error sending message: {e}")
                self.circuit_breaker.record_failure()
                self._metrics["messages_failed"] += 1
                raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get producer metrics."""
        return {
            **self._metrics,
            "circuit_breaker_state": self.circuit_breaker.state,
            "circuit_failures": self.circuit_breaker.failures
        }


# ============================================================================
# SENTIMENT-DRIVEN KAFKA PRODUCER
# ============================================================================

class SentimentDrivenKafkaProducer:
    """
    Main sentiment-driven Kafka producer.
    
    HACKATHON REQUIREMENT: Sentiment-Driven Kafka Producer
    - Analyzes sentiment of incoming messages
    - Routes 'Angry' messages to fte.tickets.urgent
    - Normal messages to fte.tickets.incoming
    """
    
    def __init__(self, kafka_config: KafkaConfig, sentiment_config: SentimentConfig):
        self.kafka_config = kafka_config
        self.sentiment_config = sentiment_config
        self.sentiment_analyzer = SentimentAnalyzer(sentiment_config)
        self.kafka_manager = KafkaProducerManager(kafka_config)
    
    async def start(self):
        """Start all services."""
        await self.kafka_manager.start()
        logger.info("✓ Sentiment-driven Kafka producer started")
    
    async def stop(self):
        """Stop all services."""
        await self.kafka_manager.stop()
        logger.info("Sentiment-driven Kafka producer stopped")
    
    async def process_gmail_message(self, message: GmailMessage):
        """
        Process Gmail webhook message.
        
        Args:
            message: Gmail message data
        """
        # Analyze sentiment
        sentiment = self.sentiment_analyzer.analyze(message.body)
        
        # Determine topic based on sentiment
        if sentiment.is_angry:
            topic = self.kafka_config.topic_tickets_urgent
            logger.info(f"😠 Angry Gmail detected - routing to URGENT topic")
        else:
            topic = self.kafka_config.topic_tickets_incoming
        
        # Create Kafka message
        kafka_message = KafkaMessage(
            event_type="gmail_inbound",
            timestamp=datetime.utcnow(),
            channel="gmail",
            message_id=message.message_id,
            customer_id=message.from_email,
            payload={
                "message_id": message.message_id,
                "thread_id": message.thread_id,
                "from": {
                    "email": message.from_email,
                    "name": message.from_name
                },
                "to": message.to,
                "subject": message.subject,
                "body": message.body,
                "received_at": message.received_at.isoformat(),
                "labels": message.labels
            },
            sentiment=sentiment,
            metadata={
                "sentiment_score": sentiment.score,
                "sentiment_label": sentiment.label.value,
                "urgency_level": sentiment.urgency_level,
                "emotional_indicators": sentiment.emotional_indicators,
                "processing_time_ms": sentiment.processing_time_ms
            }
        )
        
        # Send to Kafka
        await self.kafka_manager.send(
            topic=topic,
            value=kafka_message.model_dump(),
            key=message.from_email
        )
        
        # Publish sentiment metrics
        await self._publish_sentiment_metrics(
            message_id=message.message_id,
            channel="gmail",
            sentiment=sentiment
        )
    
    async def process_whatsapp_message(self, message: WhatsAppMessage):
        """
        Process WhatsApp webhook message.
        
        Args:
            message: WhatsApp message data
        """
        # Analyze sentiment
        sentiment = self.sentiment_analyzer.analyze(message.body)
        
        # Determine topic based on sentiment
        if sentiment.is_angry:
            topic = self.kafka_config.topic_tickets_urgent
            logger.info(f"😠 Angry WhatsApp detected - routing to URGENT topic")
        else:
            topic = self.kafka_config.topic_tickets_incoming
        
        # Create Kafka message
        kafka_message = KafkaMessage(
            event_type="whatsapp_inbound",
            timestamp=datetime.utcnow(),
            channel="whatsapp",
            message_id=message.message_sid,
            customer_id=message.from_number,
            payload={
                "message_sid": message.message_sid,
                "from": message.from_number,
                "to": message.to_number,
                "body": message.body,
                "timestamp": message.timestamp.isoformat(),
                "media_url": message.media_url
            },
            sentiment=sentiment,
            metadata={
                "sentiment_score": sentiment.score,
                "sentiment_label": sentiment.label.value,
                "urgency_level": sentiment.urgency_level,
                "emotional_indicators": sentiment.emotional_indicators,
                "processing_time_ms": sentiment.processing_time_ms
            }
        )
        
        # Send to Kafka
        await self.kafka_manager.send(
            topic=topic,
            value=kafka_message.model_dump(),
            key=message.from_number
        )
        
        # Publish sentiment metrics
        await self._publish_sentiment_metrics(
            message_id=message.message_sid,
            channel="whatsapp",
            sentiment=sentiment
        )
    
    async def process_webform_submission(self, submission: WebFormSubmission):
        """
        Process Web Form submission.
        
        Args:
            submission: Web form data
        """
        # Analyze sentiment
        sentiment = self.sentiment_analyzer.analyze(submission.message)
        
        # Determine topic based on sentiment
        if sentiment.is_angry:
            topic = self.kafka_config.topic_tickets_urgent
            logger.info(f"😠 Angry Web Form detected - routing to URGENT topic")
        else:
            topic = self.kafka_config.topic_tickets_incoming
        
        # Create Kafka message
        kafka_message = KafkaMessage(
            event_type="webform_inbound",
            timestamp=datetime.utcnow(),
            channel="web_form",
            message_id=submission.submission_id,
            customer_id=submission.email,
            payload={
                "submission_id": submission.submission_id,
                "name": submission.name,
                "email": submission.email,
                "phone": submission.phone,
                "subject": submission.subject,
                "category": submission.category,
                "message": submission.message,
                "priority": submission.priority.value,
                "submitted_at": submission.submitted_at.isoformat()
            },
            sentiment=sentiment,
            metadata={
                "sentiment_score": sentiment.score,
                "sentiment_label": sentiment.label.value,
                "urgency_level": sentiment.urgency_level,
                "emotional_indicators": sentiment.emotional_indicators,
                "processing_time_ms": sentiment.processing_time_ms
            }
        )
        
        # Send to Kafka
        await self.kafka_manager.send(
            topic=topic,
            value=kafka_message.model_dump(),
            key=submission.email
        )
        
        # Publish sentiment metrics
        await self._publish_sentiment_metrics(
            message_id=submission.submission_id,
            channel="web_form",
            sentiment=sentiment
        )
    
    async def _publish_sentiment_metrics(
        self,
        message_id: str,
        channel: str,
        sentiment: SentimentResult
    ):
        """Publish sentiment metrics to dedicated topic."""
        metrics = {
            "message_id": message_id,
            "channel": channel,
            "timestamp": datetime.utcnow().isoformat(),
            "sentiment_score": sentiment.score,
            "sentiment_label": sentiment.label.value,
            "confidence": sentiment.confidence,
            "is_angry": sentiment.is_angry,
            "urgency_level": sentiment.urgency_level,
            "emotional_indicators": sentiment.emotional_indicators,
            "processing_time_ms": sentiment.processing_time_ms
        }
        
        await self.kafka_manager.send(
            topic=self.kafka_config.topic_sentiment_metrics,
            value=metrics,
            key=message_id
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get producer metrics."""
        return {
            "kafka": self.kafka_manager.get_metrics(),
            "sentiment_analyzer": {
                "model": self.sentiment_config.model_name,
                "angry_threshold": self.sentiment_config.angry_threshold,
                "device": "cuda" if torch.cuda.is_available() else "cpu"
            }
        }


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

# Global producer instance
sentiment_producer: Optional[SentimentDrivenKafkaProducer] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global sentiment_producer
    
    # Startup
    logger.info("Starting Sentiment-Driven Kafka Producer Service...")
    sentiment_producer = SentimentDrivenKafkaProducer(KAFKA_CONFIG, SENTIMENT_CONFIG)
    await sentiment_producer.start()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Sentiment-Driven Kafka Producer Service...")
    await sentiment_producer.stop()


# Create FastAPI app
app = FastAPI(
    title="Sentiment-Driven Kafka Producer",
    description="FastAPI webhook handlers with sentiment-based Kafka routing",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# WEBHOOK ENDPOINTS
# ============================================================================

@app.post("/webhooks/gmail", status_code=status.HTTP_202_ACCEPTED)
async def gmail_webhook(
    data: GmailMessage,
    background_tasks: BackgroundTasks
):
    """
    Gmail webhook endpoint.
    
    Receives Gmail messages and routes to Kafka based on sentiment.
    """
    try:
        if not sentiment_producer:
            raise HTTPException(status_code=503, detail="Service not ready")
        
        # Process in background
        background_tasks.add_task(
            sentiment_producer.process_gmail_message,
            data
        )
        
        return {
            "status": "accepted",
            "message_id": data.message_id,
            "channel": "gmail"
        }
        
    except Exception as e:
        logger.error(f"Gmail webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhooks/whatsapp", status_code=status.HTTP_202_ACCEPTED)
async def whatsapp_webhook(
    data: WhatsAppMessage,
    background_tasks: BackgroundTasks
):
    """
    WhatsApp webhook endpoint.
    
    Receives WhatsApp messages and routes to Kafka based on sentiment.
    """
    try:
        if not sentiment_producer:
            raise HTTPException(status_code=503, detail="Service not ready")
        
        # Process in background
        background_tasks.add_task(
            sentiment_producer.process_whatsapp_message,
            data
        )
        
        return {
            "status": "accepted",
            "message_id": data.message_sid,
            "channel": "whatsapp"
        }
        
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhooks/webform", status_code=status.HTTP_202_ACCEPTED)
async def webform_webhook(
    data: WebFormSubmission,
    background_tasks: BackgroundTasks
):
    """
    Web Form webhook endpoint.
    
    Receives form submissions and routes to Kafka based on sentiment.
    """
    try:
        if not sentiment_producer:
            raise HTTPException(status_code=503, detail="Service not ready")
        
        # Process in background
        background_tasks.add_task(
            sentiment_producer.process_webform_submission,
            data
        )
        
        return {
            "status": "accepted",
            "submission_id": data.submission_id,
            "channel": "web_form"
        }
        
    except Exception as e:
        logger.error(f"Web form webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if not sentiment_producer:
        return {"status": "not_ready"}
    
    metrics = sentiment_producer.get_metrics()
    
    return {
        "status": "healthy",
        "metrics": metrics
    }


@app.get("/metrics")
async def get_metrics():
    """Get service metrics."""
    if not sentiment_producer:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    return sentiment_producer.get_metrics()


@app.post("/analyze-sentiment")
async def analyze_sentiment(text: str):
    """
    Analyze sentiment of text (utility endpoint).
    
    Args:
        text: Text to analyze
    """
    if not sentiment_producer:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    result = sentiment_producer.sentiment_analyzer.analyze(text)
    
    return result.model_dump()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 70)
    print("Sentiment-Driven Kafka Producer Service")
    print("=" * 70)
    print()
    print("Starting server on http://localhost:8001")
    print()
    print("Webhook Endpoints:")
    print("  POST /webhooks/gmail")
    print("  POST /webhooks/whatsapp")
    print("  POST /webhooks/webform")
    print()
    print("Utility Endpoints:")
    print("  GET  /health")
    print("  GET  /metrics")
    print("  POST /analyze-sentiment")
    print("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
