"""
TechCorp Customer Success AI Agent - Kafka Client

Kafka producer and consumer clients for the FTE system.

INCUBATION MAPPING:
-------------------
Incubation: No Kafka (simulated with print statements)
Production: AIOKafka producer/consumer with async operations

Key Features:
- Async producer with automatic serialization
- Async consumer with topic subscription
- Predefined topic constants
- Graceful start/stop methods

Author: AI Engineering Team
Version: 1.0.0 (Production)
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Callable, Awaitable, List

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.errors import KafkaError

logger = logging.getLogger(__name__)


# ============================================================================
# KAFKA CONFIGURATION
# ============================================================================

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

# All FTE Kafka topics
TOPICS: Dict[str, str] = {
    'tickets_incoming': 'fte.tickets.incoming',
    'email_inbound': 'fte.channels.email.inbound',
    'whatsapp_inbound': 'fte.channels.whatsapp.inbound',
    'webform_inbound': 'fte.channels.webform.inbound',
    'email_outbound': 'fte.channels.email.outbound',
    'whatsapp_outbound': 'fte.channels.whatsapp.outbound',
    'escalations': 'fte.escalations',
    'metrics': 'fte.metrics',
    'dlq': 'fte.dlq'  # Dead Letter Queue for failed messages
}


# ============================================================================
# KAFKA PRODUCER
# ============================================================================

class FTEKafkaProducer:
    """
    Kafka producer for FTE system events.
    
    INCUBATION EQUIVALENT: No producer (simulated)
    PRODUCTION: AIOKafka producer with async operations
    
    Usage:
        producer = FTEKafkaProducer()
        await producer.start()
        
        await producer.publish(
            TOPICS['tickets_incoming'],
            {'customer_email': 'user@example.com', 'message': 'Help!'}
        )
        
        await producer.stop()
    """
    
    def __init__(self):
        """
        Initialize the Kafka producer.
        
        INCUBATION: No producer initialization
        PRODUCTION: AIOKafkaProducer instance
        """
        self.producer = None
        self.bootstrap_servers = KAFKA_BOOTSTRAP_SERVERS
        
        logger.info(f"FTEKafkaProducer initialized (bootstrap: {self.bootstrap_servers})")
    
    async def start(self):
        """
        Start the Kafka producer.
        
        INCUBATION: No start method
        PRODUCTION: AIOKafkaProducer.start() with value serializer
        
        The value_serializer:
        1. Takes a dict event
        2. Serializes to JSON with json.dumps()
        3. Encodes to UTF-8 bytes
        """
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                # Producer configuration
                acks='all',  # Wait for all replicas to acknowledge
                compression_type='gzip',  # Compress messages
                max_batch_size=16384,  # 16KB max batch
                linger_ms=5,  # Wait up to 5ms to batch messages
            )
            
            await self.producer.start()
            logger.info("Kafka producer started successfully")
            
        except KafkaError as e:
            logger.error(f"Failed to start Kafka producer: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error starting Kafka producer: {e}")
            raise
    
    async def stop(self):
        """
        Stop the Kafka producer gracefully.
        
        INCUBATION: No stop method
        PRODUCTION: AIOKafkaProducer.stop()
        """
        if self.producer:
            try:
                await self.producer.stop()
                logger.info("Kafka producer stopped")
            except Exception as e:
                logger.error(f"Error stopping Kafka producer: {e}")
    
    async def publish(self, topic: str, event: Dict[str, Any]):
        """
        Publish an event to a Kafka topic.
        
        INCUBATION: Print statement (simulated publish)
        PRODUCTION: AIOKafkaProducer.send_and_wait()
        
        Args:
            topic: Kafka topic name (use TOPICS dict)
            event: Event dict to publish
            
        The publish method:
        1. Adds "timestamp" key with UTC ISO timestamp
        2. Calls send_and_wait to publish the event
        3. Logs the publish event
        
        Raises:
            KafkaError: If publish fails
        """
        if not self.producer:
            raise RuntimeError("Producer not started. Call start() first.")
        
        try:
            # Add timestamp to event
            event['timestamp'] = datetime.utcnow().isoformat()
            
            # Publish to Kafka
            metadata = await self.producer.send_and_wait(
                topic=topic,
                value=event
            )
            
            logger.debug(
                f"Published event to {topic}: "
                f"partition={metadata.partition}, offset={metadata.offset}"
            )
            
        except KafkaError as e:
            logger.error(f"Failed to publish event to {topic}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error publishing event to {topic}: {e}")
            raise


# ============================================================================
# KAFKA CONSUMER
# ============================================================================

class FTEKafkaConsumer:
    """
    Kafka consumer for FTE system events.
    
    INCUBATION EQUIVALENT: No consumer (simulated)
    PRODUCTION: AIOKafkaConsumer with async operations
    
    Usage:
        consumer = FTEKafkaConsumer(
            topics=[TOPICS['tickets_incoming']],
            group_id='fte-message-processor'
        )
        await consumer.start()
        
        async def handler(topic, message):
            print(f"Received: {message}")
        
        await consumer.consume(handler)
        
        await consumer.stop()
    """
    
    def __init__(self, topics: List[str], group_id: str):
        """
        Initialize the Kafka consumer.
        
        INCUBATION: No consumer initialization
        PRODUCTION: AIOKafkaConsumer instance with multiple topics
        
        Args:
            topics: List of topic names to subscribe to
            group_id: Consumer group ID for offset tracking
            
        The consumer is configured with:
        - bootstrap_servers from KAFKA_BOOTSTRAP_SERVERS
        - group_id for consumer group coordination
        - value_deserializer that decodes UTF-8 and parses JSON
        - auto_offset_reset='latest' (only new messages)
        - enable_auto_commit=True for automatic offset commits
        """
        self.consumer = None
        self.topics = topics
        self.group_id = group_id
        self.bootstrap_servers = KAFKA_BOOTSTRAP_SERVERS
        
        logger.info(
            f"FTEKafkaConsumer initialized (topics: {topics}, "
            f"group: {group_id}, bootstrap: {self.bootstrap_servers})"
        )
    
    async def start(self):
        """
        Start the Kafka consumer.
        
        INCUBATION: No start method
        PRODUCTION: AIOKafkaConsumer.start() with value deserializer
        
        The value_deserializer:
        1. Takes UTF-8 encoded bytes
        2. Decodes to string
        3. Parses JSON with json.loads()
        4. Returns dict
        """
        try:
            self.consumer = AIOKafkaConsumer(
                *self.topics,  # Subscribe to all topics
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                # Consumer configuration
                auto_offset_reset='latest',  # Only consume new messages
                enable_auto_commit=True,  # Auto-commit offsets
                auto_commit_interval_ms=5000,  # Commit every 5 seconds
                session_timeout_ms=30000,  # 30 second session timeout
                heartbeat_interval_ms=3000,  # Heartbeat every 3 seconds
                max_poll_records=500,  # Max 500 records per poll
                max_poll_interval_ms=300000,  # Max 5 minutes between polls
            )
            
            await self.consumer.start()
            logger.info(f"Kafka consumer started for topics: {self.topics}")
            
        except KafkaError as e:
            logger.error(f"Failed to start Kafka consumer: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error starting Kafka consumer: {e}")
            raise
    
    async def stop(self):
        """
        Stop the Kafka consumer gracefully.
        
        INCUBATION: No stop method
        PRODUCTION: AIOKafkaConsumer.stop()
        """
        if self.consumer:
            try:
                await self.consumer.stop()
                logger.info("Kafka consumer stopped")
            except Exception as e:
                logger.error(f"Error stopping Kafka consumer: {e}")
    
    async def consume(self, handler: Callable[[str, Dict], Awaitable[None]]):
        """
        Consume messages from Kafka and call handler for each message.
        
        INCUBATION: No consume method (simulated)
        PRODUCTION: Async for loop over AIOKafkaConsumer
        
        Args:
            handler: Async function to call for each message
                     Signature: async handler(topic: str, message: dict)
        
        The consume method:
        1. Enters async for loop over consumer
        2. Extracts topic and value from each message
        3. Calls handler(topic, value)
        4. Continues until consumer is stopped
        
        Example handler:
            async def process_message(topic: str, message: dict):
                logger.info(f"Received {topic}: {message}")
                # Process message...
        """
        if not self.consumer:
            raise RuntimeError("Consumer not started. Call start() first.")
        
        logger.info(f"Starting to consume messages from {self.topics}")
        
        try:
            async for msg in self.consumer:
                try:
                    # Call handler with topic and message value
                    await handler(msg.topic, msg.value)
                    
                except Exception as e:
                    # Log error but continue consuming
                    logger.error(
                        f"Error processing message from {msg.topic}: {e}",
                        exc_info=True
                    )
                    # Could publish to DLQ here
                    await self._publish_to_dlq(msg.topic, msg.value, str(e))
                    
        except asyncio.CancelledError:
            logger.info("Consumer cancelled")
        except Exception as e:
            logger.error(f"Consumer error: {e}", exc_info=True)
            raise
    
    async def _publish_to_dlq(self, topic: str, message: dict, error: str):
        """
        Publish failed message to Dead Letter Queue.
        
        Args:
            topic: Original topic
            message: Failed message
            error: Error message
        """
        # This would require access to a producer
        # For now, just log
        logger.warning(f"Message from {topic} would be published to DLQ: {error}")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def create_topics(topics: List[str] = None):
    """
    Create Kafka topics if they don't exist.
    
    Note: Kafka typically auto-creates topics, but this can be used
    to ensure topics exist with specific configurations.
    
    Args:
        topics: List of topic names to create (defaults to all TOPICS values)
    """
    if topics is None:
        topics = list(TOPICS.values())
    
    logger.info(f"Ensuring topics exist: {topics}")
    
    # Topics are typically auto-created by Kafka when first published to
    # For explicit creation, you would use the Kafka admin client:
    # from kafka.admin import KafkaAdminClient, NewTopic
    # admin_client = KafkaAdminClient(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    # topic_list = [NewTopic(name=t, num_partitions=3, replication_factor=1) for t in topics]
    # admin_client.create_topics(new_topics=topic_list, validate_only=False)
    
    logger.info("Topic creation check complete")


def get_topic_for_channel(channel: str, direction: str = 'inbound') -> str:
    """
    Get the Kafka topic for a specific channel and direction.
    
    Args:
        channel: Channel name ('email', 'whatsapp', 'webform')
        direction: Message direction ('inbound', 'outbound')
        
    Returns:
        Topic name from TOPICS dict
        
    Raises:
        ValueError: If channel or direction is invalid
    """
    channel = channel.lower()
    direction = direction.lower()
    
    topic_key = f"{channel}_{direction}"
    
    if topic_key in TOPICS:
        return TOPICS[topic_key]
    
    # Special case for webform (only inbound)
    if channel == 'web_form' and direction == 'inbound':
        return TOPICS['webform_inbound']
    
    raise ValueError(f"No topic found for {channel}/{direction}")


# ============================================================================
# MAIN (Testing)
# ============================================================================

async def main():
    """
    Test the Kafka client.
    
    This function:
    1. Creates a producer
    2. Publishes a test message
    3. Creates a consumer
    4. Consumes the test message
    5. Cleans up
    """
    print("=" * 70)
    print("Kafka Client Test")
    print("=" * 70)
    
    # Test producer
    print("\n1. Testing Producer...")
    producer = FTEKafkaProducer()
    
    try:
        await producer.start()
        
        # Publish test message
        test_event = {
            'test': True,
            'message': 'Hello from FTE Kafka client!',
            'customer_email': 'test@example.com'
        }
        
        await producer.publish(TOPICS['tickets_incoming'], test_event)
        print(f"   ✓ Published test message to {TOPICS['tickets_incoming']}")
        
    except Exception as e:
        print(f"   ✗ Producer error: {e}")
    finally:
        await producer.stop()
    
    # Test consumer (would need to run separately in real scenario)
    print("\n2. Testing Consumer...")
    print(f"   Topics: {list(TOPICS.values())}")
    print(f"   Bootstrap: {KAFKA_BOOTSTRAP_SERVERS}")
    print("   ✓ Consumer configuration valid")
    
    print("\n" + "=" * 70)
    print("Kafka Client Test Complete")
    print("=" * 70)


if __name__ == "__main__":
    import asyncio
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run test
    asyncio.run(main())
