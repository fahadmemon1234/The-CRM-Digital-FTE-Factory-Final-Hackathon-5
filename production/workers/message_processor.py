"""
TechCorp Customer Success AI Agent - Kafka Message Processor

Unified message processor that consumes incoming tickets from Kafka,
processes them through the AI agent, and stores responses.

INCUBATION MAPPING:
-------------------
Incubation: Single-threaded process_message() in prototype.py
Production: Async Kafka consumer with unified processing pipeline

Key Features:
- Unified processing for all channels (email, whatsapp, web_form)
- Customer resolution across channels
- Conversation continuity tracking
- Agent execution with context
- Metrics publishing
- Error handling with auto-escalation

Author: AI Engineering Team
Version: 1.0.0 (Production)
"""

import asyncio
import logging
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from agents import Runner

from production.channels.gmail_handler import GmailHandler
from production.channels.whatsapp_handler import WhatsAppHandler
from production.agent.customer_success_agent import (
    customer_success_agent,
    Channel,
    KnowledgeSearchInput,
    TicketInput,
    EscalationInput,
    ResponseInput,
)
from production.database.queries import (
    get_db_pool,
    find_customer_by_email,
    find_customer_by_phone,
    create_customer,
    add_customer_identifier,
    create_conversation,
    store_message,
    get_conversation_history,
)
from production.channels.web_form_handler import publish_to_kafka

# Import Kafka configuration
try:
    from production.kafka_client import (
        FTEKafkaProducer,
        FTEKafkaConsumer,
        TOPICS,
    )
    HAS_KAFKA = True
except ImportError:
    HAS_KAFKA = False
    logger = logging.getLogger(__name__)
    logger.warning("Kafka client not available, using mock producer")

logger = logging.getLogger(__name__)


class UnifiedMessageProcessor:
    """
    Unified message processor for all customer communication channels.
    
    INCUBATION EQUIVALENT: CustomerSuccessAgent.process_message() in prototype.py
    PRODUCTION: Kafka-based async processor with channel handlers
    
    This processor:
    1. Consumes messages from Kafka topics
    2. Resolves customer identity across channels
    3. Creates/retrieves conversations
    4. Runs the AI agent
    5. Stores responses
    6. Publishes metrics
    7. Handles errors with auto-escalation
    """
    
    def __init__(self):
        """
        Initialize the message processor.
        
        INCUBATION: No initialization (direct function calls)
        PRODUCTION: Channel handlers, Kafka producer/consumer initialization
        """
        self.gmail_handler = None
        self.whatsapp_handler = None
        self.kafka_producer = None
        self.kafka_consumer = None
        self.db_pool = None
        
        # Processing statistics
        self.stats = {
            'messages_processed': 0,
            'errors': 0,
            'escalations': 0,
            'start_time': None
        }
        
        logger.info("UnifiedMessageProcessor initialized")
    
    async def start(self):
        """
        Start the message processor.
        
        INCUBATION: No start method (synchronous execution)
        PRODUCTION: Async Kafka consumer with continuous processing
        
        This method:
        1. Starts Kafka producer
        2. Creates consumer for incoming tickets topic
        3. Starts consuming messages
        4. Calls process_message for each message
        """
        logger.info("Starting message processor...")
        
        # Initialize channel handlers
        try:
            credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
            self.gmail_handler = GmailHandler(credentials_path)
            logger.info("GmailHandler initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize GmailHandler: {e}")
        
        try:
            self.whatsapp_handler = WhatsAppHandler()
            logger.info("WhatsAppHandler initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize WhatsAppHandler: {e}")
        
        # Start Kafka producer
        if HAS_KAFKA:
            self.kafka_producer = FTEKafkaProducer()
            await self.kafka_producer.start()
            logger.info("Kafka producer started")
        
        # Create Kafka consumer for incoming tickets
        if HAS_KAFKA:
            self.kafka_consumer = FTEKafkaConsumer(
                topics=[TOPICS['tickets_incoming']],
                group_id='fte-message-processor'
            )
            await self.kafka_consumer.start()
            logger.info(f"Kafka consumer started for topic: {TOPICS['tickets_incoming']}")
            
            # Start consuming
            logger.info("Message processor started, listening for tickets...")
            await self.kafka_consumer.consume(self.process_message)
        else:
            logger.warning("Kafka not available, processor running in mock mode")
        
        self.stats['start_time'] = datetime.utcnow()
    
    async def process_message(self, topic: str, message: dict):
        """
        Process an incoming message from Kafka.
        
        INCUBATION: process_message() in prototype.py
        PRODUCTION: Full async pipeline with Kafka, DB, and agent
        
        Processing pipeline:
        1. Record start time for latency tracking
        2. Extract channel from message
        3. Resolve customer identity
        4. Get or create conversation
        5. Store inbound message
        6. Load conversation history
        7. Run AI agent
        8. Calculate latency
        9. Store agent response
        10. Publish metrics
        11. Log completion
        
        Args:
            topic: Kafka topic name
            message: Message dict from Kafka
        """
        start_time = time.time()
        
        try:
            # Extract channel
            channel = Channel(message.get('channel', 'web_form'))
            logger.info(f"Processing {channel.value} message from {message.get('customer_email', 'unknown')}")
            
            # Resolve customer identity
            customer_id = await self.resolve_customer(message)
            logger.info(f"Resolved customer: {customer_id}")
            
            # Get or create conversation
            conversation_id = await self.get_or_create_conversation(
                customer_id, channel, message
            )
            logger.info(f"Conversation: {conversation_id}")
            
            # Store inbound message
            channel_message_id = message.get('channel_message_id')
            await self.store_message(
                conversation_id=conversation_id,
                channel=channel.value,
                direction='inbound',
                role='customer',
                content=message.get('content', ''),
                channel_message_id=channel_message_id,
                metadata=message.get('metadata', {})
            )
            
            # Load conversation history
            history = await self.load_conversation_history(conversation_id)
            
            # Build context for agent
            context = {
                'customer_id': customer_id,
                'conversation_id': conversation_id,
                'channel': channel.value,
                'ticket_subject': message.get('subject', ''),
                'metadata': message.get('metadata', {})
            }
            
            # Run AI agent
            logger.info("Running customer_success_agent...")
            result = await Runner.run(
                customer_success_agent,
                input=history,
                context=context
            )
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Store agent response
            response_content = result.final_output if hasattr(result, 'final_output') else str(result)
            await self.store_message(
                conversation_id=conversation_id,
                channel=channel.value,
                direction='outbound',
                role='agent',
                content=response_content,
                latency_ms=int(latency_ms),
                tool_calls=self._extract_tool_calls(result)
            )
            
            # Publish metrics
            await self._publish_metrics(
                channel=channel.value,
                latency_ms=latency_ms,
                success=True
            )
            
            # Log completion
            logger.info(f"Processed {channel.value} message in {latency_ms:.0f}ms")
            self.stats['messages_processed'] += 1
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            self.stats['errors'] += 1
            await self.handle_error(message, e)
    
    async def resolve_customer(self, message: dict) -> str:
        """
        Resolve customer identity from message.
        
        INCUBATION: Simple dict lookup in prototype.py
        PRODUCTION: Database query with cross-channel identity resolution
        
        Resolution order:
        1. Try by email (primary identifier)
        2. Try by phone (for WhatsApp)
        3. Create new customer if not found
        
        Args:
            message: Message dict with customer_email or customer_phone
            
        Returns:
            Customer UUID as string
            
        Raises:
            ValueError: If neither email nor phone provided
        """
        # Try by email first
        customer_email = message.get('customer_email')
        if customer_email:
            customer = await find_customer_by_email(customer_email)
            if customer:
                logger.info(f"Found customer by email: {customer_email}")
                return customer['id']
            
            # Create new customer
            logger.info(f"Creating new customer: {customer_email}")
            customer_id = await create_customer(
                email=customer_email,
                name=message.get('customer_name', ''),
                phone=message.get('customer_phone')
            )
            return customer_id
        
        # Try by phone for WhatsApp
        customer_phone = message.get('customer_phone')
        if customer_phone:
            customer = await find_customer_by_phone(customer_phone)
            if customer:
                logger.info(f"Found customer by phone: {customer_phone}")
                return customer['id']
            
            # Create new customer with phone identifier
            logger.info(f"Creating new customer with phone: {customer_phone}")
            customer_id = await create_customer(
                email=f"{customer_phone}@whatsapp.local",
                name=message.get('customer_name', ''),
                phone=customer_phone
            )
            
            # Add WhatsApp identifier
            await add_customer_identifier(
                customer_id=customer_id,
                identifier_type='whatsapp',
                identifier_value=customer_phone,
                verified=False
            )
            
            return customer_id
        
        # Neither email nor phone provided
        raise ValueError("Message must contain customer_email or customer_phone")
    
    async def get_or_create_conversation(
        self,
        customer_id: str,
        channel: Channel,
        message: dict
    ) -> str:
        """
        Get existing active conversation or create new one.
        
        INCUBATION: ConversationState dict in prototype.py
        PRODUCTION: Database query with 24-hour activity window
        
        Args:
            customer_id: Customer UUID
            channel: Communication channel
            message: Message dict
            
        Returns:
            Conversation UUID as string
        """
        pool = await get_db_pool()
        
        if not pool:
            # Mock mode: generate conversation ID
            conversation_id = f"conv_{uuid.uuid4().hex[:12]}"
            logger.warning(f"DB not available, generated mock conversation: {conversation_id}")
            return conversation_id
        
        try:
            async with pool.acquire() as conn:
                # Check for active conversation in last 24 hours
                row = await conn.fetchrow("""
                    SELECT id
                    FROM conversations
                    WHERE customer_id = $1
                    AND status = 'active'
                    AND started_at > NOW() - INTERVAL '24 hours'
                    ORDER BY started_at DESC
                    LIMIT 1
                """, customer_id)
                
                if row:
                    conversation_id = str(row['id'])
                    logger.info(f"Found active conversation: {conversation_id}")
                    return conversation_id
                
                # Create new conversation
                conversation_id = await create_conversation(
                    customer_id=customer_id,
                    channel=channel.value,
                    metadata={
                        'subject': message.get('subject', ''),
                        'category': message.get('category'),
                        'priority': message.get('priority', 'medium')
                    }
                )
                logger.info(f"Created new conversation: {conversation_id}")
                return conversation_id
                
        except Exception as e:
            logger.error(f"Error getting/creating conversation: {e}")
            # Fallback: generate conversation ID
            return f"conv_{uuid.uuid4().hex[:12]}"
    
    async def load_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Load conversation history for agent context.
        
        INCUBATION: state.messages list in prototype.py
        PRODUCTION: Database query with message formatting
        
        Args:
            conversation_id: Conversation UUID
            
        Returns:
            List of message dicts formatted for agent
        """
        history = await get_conversation_history(conversation_id)
        
        # Format for agent
        formatted_history = []
        for msg in history:
            formatted_history.append({
                'role': msg['role'],
                'content': msg['content'],
                'channel': msg['channel'],
                'timestamp': msg['created_at']
            })
        
        return formatted_history
    
    async def store_message(
        self,
        conversation_id: str,
        channel: str,
        direction: str,
        role: str,
        content: str,
        channel_message_id: Optional[str] = None,
        latency_ms: Optional[int] = None,
        tool_calls: Optional[List[Dict]] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Store message in database.
        
        INCUBATION: state.messages.append() in prototype.py
        PRODUCTION: Database insert with full metadata
        
        Args:
            conversation_id: Conversation UUID
            channel: Message channel
            direction: 'inbound' or 'outbound'
            role: 'customer', 'agent', or 'system'
            content: Message content
            channel_message_id: External channel message ID
            latency_ms: Response latency (for agent messages)
            tool_calls: Tools invoked (for agent messages)
            metadata: Additional metadata
            
        Returns:
            Message UUID as string
        """
        return await store_message(
            conversation_id=conversation_id,
            channel=channel,
            direction=direction,
            role=role,
            content=content,
            tokens_used=None,
            latency_ms=latency_ms,
            tool_calls=tool_calls,
            channel_message_id=channel_message_id,
            delivery_status='delivered' if direction == 'outbound' else 'received'
        )
    
    def _extract_tool_calls(self, result) -> List[Dict]:
        """
        Extract tool calls from agent result.
        
        Args:
            result: Agent run result
            
        Returns:
            List of tool call dicts
        """
        tool_calls = []
        
        if hasattr(result, 'tool_calls') and result.tool_calls:
            for tc in result.tool_calls:
                tool_calls.append({
                    'tool': getattr(tc, 'name', 'unknown'),
                    'arguments': getattr(tc, 'arguments', {})
                })
        
        return tool_calls
    
    async def _publish_metrics(
        self,
        channel: str,
        latency_ms: float,
        success: bool
    ):
        """
        Publish processing metrics to Kafka.
        
        INCUBATION: No metrics (print statements only)
        PRODUCTION: Kafka events for analytics
        
        Args:
            channel: Message channel
            latency_ms: Processing latency
            success: Whether processing succeeded
        """
        if not HAS_KAFKA or not self.kafka_producer:
            return
        
        metrics_event = {
            'event_type': 'message_processed',
            'channel': channel,
            'latency_ms': latency_ms,
            'success': success,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.kafka_producer.send(
            TOPICS['metrics'],
            metrics_event
        )
    
    async def handle_error(self, message: dict, error: Exception):
        """
        Handle processing errors with apology and escalation.
        
        INCUBATION: Simple exception handling in prototype.py
        PRODUCTION: Auto-escalation with apology message
        
        Error handling:
        1. Build apology message
        2. Try to send apology via correct channel
        3. Publish error event to escalations topic
        4. Log the failure
        
        Args:
            message: Original message dict
            error: Exception that occurred
        """
        logger.error(f"Handling error: {error}")
        
        # Build apology message
        apology = "I'm sorry, I'm having trouble processing your request right now. " \
                  "A human agent will follow up shortly."
        
        # Try to send apology via correct channel
        channel = message.get('channel', 'web_form')
        
        try:
            if channel == 'email' and self.gmail_handler:
                customer_email = message.get('customer_email')
                if customer_email:
                    await self.gmail_handler.send_reply(
                        to_email=customer_email,
                        subject="Re: " + message.get('subject', 'Support Request'),
                        body=apology
                    )
                    logger.info(f"Sent apology email to {customer_email}")
                    
            elif channel == 'whatsapp' and self.whatsapp_handler:
                customer_phone = message.get('customer_phone')
                if customer_phone:
                    await self.whatsapp_handler.send_message(
                        to_phone=customer_phone,
                        body=apology
                    )
                    logger.info(f"Sent apology WhatsApp to {customer_phone}")
                    
        except Exception as send_error:
            logger.error(f"Failed to send apology: {send_error}")
        
        # Publish error event to escalations topic
        if HAS_KAFKA and self.kafka_producer:
            error_event = {
                'event_type': 'processing_error',
                'original_message': message,
                'error': str(error),
                'error_type': type(error).__name__,
                'requires_human': True,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            await self.kafka_producer.send(
                TOPICS['escalations'],
                error_event
            )
            logger.info("Published error event to escalations topic")
            self.stats['escalations'] += 1
    
    async def stop(self):
        """Stop the message processor and clean up resources."""
        logger.info("Stopping message processor...")
        
        if self.kafka_consumer:
            await self.kafka_consumer.stop()
        
        if self.kafka_producer:
            await self.kafka_producer.stop()
        
        if self.gmail_handler:
            await self.gmail_handler.close()
        
        if self.whatsapp_handler:
            await self.whatsapp_handler.close()
        
        # Log final statistics
        if self.stats['start_time']:
            uptime = datetime.utcnow() - self.stats['start_time']
            logger.info(f"Processor uptime: {uptime}")
        
        logger.info(
            f"Final stats: processed={self.stats['messages_processed']}, "
            f"errors={self.stats['errors']}, escalations={self.stats['escalations']}"
        )


async def main():
    """
    Main entry point for the message processor.
    
    INCUBATION: No main function (direct execution)
    PRODUCTION: Async main with graceful shutdown
    """
    processor = UnifiedMessageProcessor()
    
    try:
        await processor.start()
        
        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Processor error: {e}", exc_info=True)
    finally:
        await processor.stop()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run processor
    asyncio.run(main())
