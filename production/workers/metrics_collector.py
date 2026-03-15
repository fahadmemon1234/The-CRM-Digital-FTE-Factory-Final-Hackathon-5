"""
TechCorp Customer Success AI Agent - Metrics Collector

Aggregates and stores processing metrics from Kafka.

INCUBATION MAPPING:
-------------------
Incubation: No metrics collection (print statements only)
Production: Kafka consumer with periodic aggregation and database storage

Key Features:
- Real-time metrics aggregation from Kafka
- Per-channel metrics (messages, latency, escalation rate)
- Periodic database storage (every 5 minutes)
- Running averages and counts

Author: AI Engineering Team
Version: 1.0.0 (Production)
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from collections import defaultdict

from production.database.queries import (
    get_db_pool,
    record_metric,
)

try:
    from production.kafka_client import (
        FTEKafkaConsumer,
        TOPICS,
    )
    HAS_KAFKA = True
except ImportError:
    HAS_KAFKA = False
    logger = logging.getLogger(__name__)
    logger.warning("Kafka client not available, metrics collector running in mock mode")

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Metrics collector that aggregates and stores processing metrics.
    
    INCUBATION EQUIVALENT: No metrics collection
    PRODUCTION: Kafka consumer with periodic aggregation
    
    This collector:
    1. Consumes metrics events from Kafka
    2. Aggregates per-channel statistics
    3. Stores aggregated metrics to database every 5 minutes
    4. Tracks: messages_per_channel, avg_latency, escalation_rate
    """
    
    # Aggregation interval in seconds
    AGGREGATION_INTERVAL = 300  # 5 minutes
    
    def __init__(self):
        """Initialize the metrics collector."""
        self.kafka_consumer = None
        self.db_pool = None
        
        # Running metrics
        self.metrics = {
            'messages_per_channel': defaultdict(int),
            'latency_sum_per_channel': defaultdict(float),
            'latency_count_per_channel': defaultdict(int),
            'escalations_per_channel': defaultdict(int),
            'errors': 0,
            'start_time': None
        }
        
        # Aggregated metrics for storage
        self.aggregated = {}
        
        logger.info("MetricsCollector initialized")
    
    async def start(self):
        """
        Start the metrics collector.
        
        This method:
        1. Creates Kafka consumer for metrics topic
        2. Starts consuming metrics events
        3. Starts periodic aggregation task
        """
        logger.info("Starting metrics collector...")
        
        if HAS_KAFKA:
            self.kafka_consumer = FTEKafkaConsumer(
                topics=[TOPICS['metrics']],
                group_id='fte-metrics-collector'
            )
            await self.kafka_consumer.start()
            logger.info(f"Kafka consumer started for topic: {TOPICS['metrics']}")
            
            # Start consuming
            await self.kafka_consumer.consume(self._process_metric_event)
        else:
            logger.warning("Kafka not available, collector running in mock mode")
        
        self.metrics['start_time'] = datetime.utcnow()
        
        # Start periodic aggregation task
        asyncio.create_task(self._periodic_aggregation())
        
        logger.info("Metrics collector started")
    
    async def _process_metric_event(self, topic: str, event: dict):
        """
        Process a single metric event from Kafka.
        
        Args:
            topic: Kafka topic name
            event: Metric event dict
        """
        try:
            event_type = event.get('event_type')
            channel = event.get('channel', 'unknown')
            timestamp = event.get('timestamp', datetime.utcnow().isoformat())
            
            if event_type == 'message_processed':
                # Count message
                self.metrics['messages_per_channel'][channel] += 1
                
                # Track latency
                latency_ms = event.get('latency_ms', 0)
                if latency_ms:
                    self.metrics['latency_sum_per_channel'][channel] += latency_ms
                    self.metrics['latency_count_per_channel'][channel] += 1
                
                # Track success/failure
                if not event.get('success', True):
                    self.metrics['errors'] += 1
                    self.metrics['escalations_per_channel'][channel] += 1
                    
            elif event_type == 'escalation':
                self.metrics['escalations_per_channel'][channel] += 1
            
            logger.debug(f"Processed metric event: {event_type} for {channel}")
            
        except Exception as e:
            logger.error(f"Error processing metric event: {e}")
    
    async def _periodic_aggregation(self):
        """
        Periodically aggregate and store metrics.
        
        Runs every AGGREGATION_INTERVAL seconds (5 minutes).
        """
        while True:
            try:
                await asyncio.sleep(self.AGGREGATION_INTERVAL)
                await self._aggregate_and_store()
                
            except Exception as e:
                logger.error(f"Error in periodic aggregation: {e}", exc_info=True)
    
    async def _aggregate_and_store(self):
        """
        Aggregate current metrics and store to database.
        
        This method:
        1. Calculates averages and rates
        2. Stores to agent_metrics table
        3. Resets running counters
        """
        logger.info("Aggregating and storing metrics...")
        
        current_time = datetime.utcnow()
        
        # Calculate aggregated metrics
        aggregated = {
            'timestamp': current_time.isoformat(),
            'channels': {}
        }
        
        # Get all channels
        all_channels = set(self.metrics['messages_per_channel'].keys())
        
        for channel in all_channels:
            messages = self.metrics['messages_per_channel'][channel]
            escalations = self.metrics['escalations_per_channel'][channel]
            
            # Calculate average latency
            latency_count = self.metrics['latency_count_per_channel'][channel]
            if latency_count > 0:
                avg_latency = self.metrics['latency_sum_per_channel'][channel] / latency_count
            else:
                avg_latency = 0
            
            # Calculate escalation rate
            escalation_rate = (escalations / messages * 100) if messages > 0 else 0
            
            aggregated['channels'][channel] = {
                'messages': messages,
                'avg_latency_ms': round(avg_latency, 2),
                'escalations': escalations,
                'escalation_rate': round(escalation_rate, 2)
            }
        
        # Store to database
        await self._store_metrics(aggregated)
        
        # Store aggregated for access
        self.aggregated = aggregated
        
        # Reset running counters
        self._reset_counters()
        
        logger.info(f"Stored metrics for {len(all_channels)} channels")
    
    async def _store_metrics(self, aggregated: dict):
        """
        Store aggregated metrics to database.
        
        Args:
            aggregated: Aggregated metrics dict
        """
        pool = await get_db_pool()
        
        if not pool:
            logger.warning("Database not available, skipping metrics storage")
            return
        
        timestamp = aggregated.get('timestamp', datetime.utcnow().isoformat())
        
        try:
            for channel, metrics in aggregated.get('channels', {}).items():
                # Store messages count
                await record_metric(
                    metric_name='messages_per_channel',
                    metric_value=metrics['messages'],
                    channel=channel,
                    dimensions={'period': '5min'}
                )
                
                # Store average latency
                await record_metric(
                    metric_name='avg_latency_ms',
                    metric_value=metrics['avg_latency_ms'],
                    channel=channel,
                    dimensions={'period': '5min'}
                )
                
                # Store escalation rate
                await record_metric(
                    metric_name='escalation_rate',
                    metric_value=metrics['escalation_rate'],
                    channel=channel,
                    dimensions={'period': '5min'}
                )
                
                # Store escalation count
                await record_metric(
                    metric_name='escalations_per_channel',
                    metric_value=metrics['escalations'],
                    channel=channel,
                    dimensions={'period': '5min'}
                )
            
            # Store total errors
            await record_metric(
                metric_name='total_errors',
                metric_value=self.metrics.get('errors', 0),
                channel='all',
                dimensions={'period': '5min'}
            )
            
            logger.info("Metrics stored to database")
            
        except Exception as e:
            logger.error(f"Failed to store metrics: {e}")
    
    def _reset_counters(self):
        """Reset running metric counters."""
        self.metrics['messages_per_channel'] = defaultdict(int)
        self.metrics['latency_sum_per_channel'] = defaultdict(float)
        self.metrics['latency_count_per_channel'] = defaultdict(int)
        self.metrics['escalations_per_channel'] = defaultdict(int)
        self.metrics['errors'] = 0
    
    def get_current_metrics(self) -> dict:
        """
        Get current aggregated metrics.
        
        Returns:
            Dict with current metrics
        """
        return self.aggregated
    
    def get_summary(self) -> dict:
        """
        Get summary of metrics since start.
        
        Returns:
            Dict with summary statistics
        """
        total_messages = sum(self.metrics['messages_per_channel'].values())
        total_escalations = sum(self.metrics['escalations_per_channel'].values())
        
        # Calculate overall average latency
        total_latency = sum(self.metrics['latency_sum_per_channel'].values())
        total_latency_count = sum(self.metrics['latency_count_per_channel'].values())
        overall_avg_latency = total_latency / total_latency_count if total_latency_count > 0 else 0
        
        # Calculate overall escalation rate
        overall_escalation_rate = (total_escalations / total_messages * 100) if total_messages > 0 else 0
        
        uptime = datetime.utcnow() - self.metrics['start_time'] if self.metrics['start_time'] else timedelta(0)
        
        return {
            'total_messages': total_messages,
            'total_escalations': total_escalations,
            'overall_escalation_rate': round(overall_escalation_rate, 2),
            'overall_avg_latency_ms': round(overall_avg_latency, 2),
            'total_errors': self.metrics['errors'],
            'uptime': str(uptime),
            'messages_per_channel': dict(self.metrics['messages_per_channel']),
            'start_time': self.metrics['start_time'].isoformat() if self.metrics['start_time'] else None
        }
    
    async def stop(self):
        """Stop the metrics collector and store final metrics."""
        logger.info("Stopping metrics collector...")
        
        # Store final metrics before stopping
        await self._aggregate_and_store()
        
        if self.kafka_consumer:
            await self.kafka_consumer.stop()
        
        logger.info("Metrics collector stopped")


async def main():
    """
    Main entry point for the metrics collector.
    """
    collector = MetricsCollector()
    
    try:
        await collector.start()
        
        # Keep running and print summary periodically
        while True:
            await asyncio.sleep(60)  # Print summary every minute
            
            summary = collector.get_summary()
            logger.info(f"Metrics summary: {summary}")
            
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Collector error: {e}", exc_info=True)
    finally:
        await collector.stop()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run collector
    asyncio.run(main())
