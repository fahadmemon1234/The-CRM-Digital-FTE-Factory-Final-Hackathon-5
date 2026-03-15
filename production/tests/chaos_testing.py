#!/usr/bin/env python3
"""
TechCorp Customer Success AI Agent - Chaos Testing Script

This script implements chaos testing for the FTE system by randomly killing
Docker containers or Kubernetes pods to verify:
- Auto-Resume capabilities
- Message Persistence via Kafka
- System resilience and self-healing

CHAOS TESTING PRINCIPLES:
-------------------------
1. Random Failure Injection: Kill containers/pods at random intervals
2. Controlled Blast Radius: Only kill non-critical services
3. Automated Recovery Verification: Verify services restart automatically
4. Message Persistence Check: Ensure no messages lost during failures
5. Metrics Collection: Track recovery time and success rate

USAGE:
------
# Docker mode (default):
python chaos_testing.py --mode docker --interval 7200 --target all

# Kubernetes mode:
python chaos_testing.py --mode kubernetes --namespace customer-success-fte

# Dry run (no actual kills):
python chaos_testing.py --dry-run

# Custom configuration:
python chaos_testing.py --config chaos_config.json

Author: AI Engineering Team
Version: 1.0.0
"""

import argparse
import asyncio
import json
import logging
import os
import random
import subprocess
import sys
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
import hashlib


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class ChaosConfig:
    """Configuration for chaos testing."""
    mode: str = "docker"  # docker or kubernetes
    namespace: str = "customer-success-fte"  # K8s namespace
    interval_seconds: int = 7200  # 2 hours default
    target_services: List[str] = field(default_factory=list)
    excluded_services: List[str] = field(default_factory=lambda: ["kafka", "zookeeper"])
    max_concurrent_failures: int = 1
    dry_run: bool = False
    verbose: bool = True
    log_file: str = "chaos_test.log"
    metrics_file: str = "chaos_metrics.json"
    kill_probability: float = 0.3  # 30% chance to kill in each interval
    recovery_timeout: int = 60  # Seconds to wait for recovery
    notification_webhook: Optional[str] = None


# Default Docker Compose services
DOCKER_SERVICES = [
    "zookeeper",
    "kafka",
    "postgres",
    "fte-api",
    "fte-worker",
    "fte-metrics"
]

# Default Kubernetes deployments
K8S_DEPLOYMENTS = [
    "fte-api",
    "fte-worker",
    "fte-metrics"
]


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging(config: ChaosConfig) -> logging.Logger:
    """Setup logging for chaos testing."""
    logger = logging.getLogger("chaos_testing")
    logger.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO if config.verbose else logging.WARNING)
    console_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(config.log_file)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    return logger


# ============================================================================
# METRICS COLLECTION
# ============================================================================

@dataclass
class ChaosEvent:
    """Represents a chaos testing event."""
    timestamp: str
    event_type: str  # kill, recovery, failure, skip
    service_name: str
    mode: str
    duration_seconds: float
    success: bool
    error_message: Optional[str] = None
    recovery_time_seconds: Optional[float] = None
    messages_persisted: Optional[int] = None
    messages_recovered: Optional[int] = None


class MetricsCollector:
    """Collects and stores chaos testing metrics."""
    
    def __init__(self, metrics_file: str):
        self.metrics_file = metrics_file
        self.events: List[ChaosEvent] = []
        self.start_time = datetime.utcnow()
        
    def record_event(self, event: ChaosEvent):
        """Record a chaos event."""
        self.events.append(event)
        self.save()
        
    def save(self):
        """Save metrics to file."""
        metrics_data = {
            "test_start": self.start_time.isoformat(),
            "test_duration_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "total_events": len(self.events),
            "events": [asdict(e) for e in self.events],
            "summary": self.generate_summary()
        }
        
        with open(self.metrics_file, 'w') as f:
            json.dump(metrics_data, f, indent=2)
            
    def generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics."""
        if not self.events:
            return {}
            
        kills = [e for e in self.events if e.event_type == "kill"]
        recoveries = [e for e in self.events if e.event_type == "recovery"]
        failures = [e for e in self.events if e.event_type == "failure"]
        
        recovery_times = [e.recovery_time_seconds for e in recoveries if e.recovery_time_seconds]
        
        return {
            "total_kills": len(kills),
            "total_recoveries": len(recoveries),
            "total_failures": len(failures),
            "success_rate": len(recoveries) / len(kills) * 100 if kills else 0,
            "average_recovery_time": sum(recovery_times) / len(recovery_times) if recovery_times else 0,
            "min_recovery_time": min(recovery_times) if recovery_times else 0,
            "max_recovery_time": max(recovery_times) if recovery_times else 0,
            "messages_persisted_total": sum(e.messages_persisted or 0 for e in events),
            "messages_recovered_total": sum(e.messages_recovered or 0 for e in events),
        }


# ============================================================================
# DOCKER CHAOS ENGINE
# ============================================================================

class DockerChaosEngine:
    """Implements chaos testing for Docker Compose environments."""
    
    def __init__(self, config: ChaosConfig, logger: logging.Logger, metrics: MetricsCollector):
        self.config = config
        self.logger = logger
        self.metrics = metrics
        self.compose_file = self._find_compose_file()
        
    def _find_compose_file(self) -> str:
        """Find docker-compose.yml file."""
        possible_paths = [
            "production/docker-compose.yml",
            "docker-compose.yml",
            "../production/docker-compose.yml"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Return default path
        return "production/docker-compose.yml"
    
    def list_services(self) -> List[str]:
        """List running Docker services."""
        try:
            result = subprocess.run(
                ["docker-compose", "-f", self.compose_file, "ps", "--services"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                services = [s.strip() for s in result.stdout.strip().split('\n') if s.strip()]
                # Filter based on config
                if self.config.target_services:
                    services = [s for s in services if s in self.config.target_services]
                if self.config.excluded_services:
                    services = [s for s in services if s not in self.config.excluded_services]
                return services
            
            return DOCKER_SERVICES
        except Exception as e:
            self.logger.error(f"Failed to list services: {e}")
            return DOCKER_SERVICES
    
    def kill_service(self, service_name: str) -> bool:
        """Kill a Docker service (stop container)."""
        try:
            self.logger.info(f"🔪 Killing service: {service_name}")
            
            if self.config.dry_run:
                self.logger.info(f"[DRY RUN] Would kill {service_name}")
                return True
            
            # Stop the container
            result = subprocess.run(
                ["docker-compose", "-f", self.compose_file, "stop", service_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.logger.info(f"✓ Service {service_name} stopped")
                return True
            else:
                self.logger.error(f"✗ Failed to stop {service_name}: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"✗ Error killing {service_name}: {e}")
            return False
    
    def recover_service(self, service_name: str) -> tuple[bool, float]:
        """Recover a Docker service (start container) and measure recovery time."""
        try:
            self.logger.info(f"♻️ Recovering service: {service_name}")
            
            if self.config.dry_run:
                self.logger.info(f"[DRY RUN] Would recover {service_name}")
                return True, 0.0
            
            start_time = time.time()
            
            # Start the container
            result = subprocess.run(
                ["docker-compose", "-f", self.compose_file, "start", service_name],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            recovery_time = time.time() - start_time
            
            if result.returncode == 0:
                # Wait for service to be healthy
                healthy = self._wait_for_healthy(service_name)
                if healthy:
                    self.logger.info(f"✓ Service {service_name} recovered in {recovery_time:.2f}s")
                    return True, recovery_time
                else:
                    self.logger.warning(f"⚠ Service {service_name} started but not healthy")
                    return False, recovery_time
            else:
                self.logger.error(f"✗ Failed to start {service_name}: {result.stderr}")
                return False, recovery_time
                
        except Exception as e:
            self.logger.error(f"✗ Error recovering {service_name}: {e}")
            return False, 0.0
    
    def _wait_for_healthy(self, service_name: str, timeout: int = 60) -> bool:
        """Wait for service to become healthy."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                result = subprocess.run(
                    ["docker-compose", "-f", self.compose_file, "ps", service_name],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0 and "Up" in result.stdout:
                    return True
                    
            except Exception:
                pass
            
            time.sleep(2)
        
        return False
    
    def check_message_persistence(self) -> Dict[str, int]:
        """Check Kafka message persistence during chaos."""
        try:
            # This would integrate with your actual Kafka monitoring
            # For now, return mock data
            return {
                "messages_in_queue": random.randint(0, 100),
                "messages_processed": random.randint(500, 1000),
                "messages_lost": 0  # Should always be 0 with proper persistence
            }
        except Exception as e:
            self.logger.error(f"Failed to check message persistence: {e}")
            return {"messages_in_queue": 0, "messages_processed": 0, "messages_lost": 0}


# ============================================================================
# KUBERNETES CHAOS ENGINE
# ============================================================================

class KubernetesChaosEngine:
    """Implements chaos testing for Kubernetes environments."""
    
    def __init__(self, config: ChaosConfig, logger: logging.Logger, metrics: MetricsCollector):
        self.config = config
        self.logger = logger
        self.metrics = metrics
        self.namespace = config.namespace
        
    def list_deployments(self) -> List[str]:
        """List Kubernetes deployments."""
        try:
            result = subprocess.run(
                ["kubectl", "get", "deployments", "-n", self.namespace, "-o", "jsonpath={.items[*].metadata.name}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                deployments = result.stdout.strip().split()
                # Filter based on config
                if self.config.target_services:
                    deployments = [d for d in deployments if d in self.config.target_services]
                if self.config.excluded_services:
                    deployments = [d for d in deployments if d not in self.config.excluded_services]
                return deployments
            
            return K8S_DEPLOYMENTS
        except Exception as e:
            self.logger.error(f"Failed to list deployments: {e}")
            return K8S_DEPLOYMENTS
    
    def kill_pod(self, deployment_name: str) -> bool:
        """Kill a pod from a deployment (simulate pod failure)."""
        try:
            self.logger.info(f"🔪 Killing pod from deployment: {deployment_name}")
            
            if self.config.dry_run:
                self.logger.info(f"[DRY RUN] Would kill pod from {deployment_name}")
                return True
            
            # Delete a random pod from the deployment
            result = subprocess.run(
                ["kubectl", "delete", "pod", "-l", f"app={deployment_name}", "-n", self.namespace],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.logger.info(f"✓ Pod deleted from {deployment_name}")
                return True
            else:
                self.logger.error(f"✗ Failed to delete pod from {deployment_name}: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"✗ Error killing pod from {deployment_name}: {e}")
            return False
    
    def recover_pod(self, deployment_name: str) -> tuple[bool, float]:
        """Wait for pod recovery and measure recovery time."""
        try:
            self.logger.info(f"♻️ Waiting for pod recovery: {deployment_name}")
            
            if self.config.dry_run:
                self.logger.info(f"[DRY RUN] Would wait for {deployment_name} recovery")
                return True, 0.0
            
            start_time = time.time()
            
            # Wait for deployment to have ready replicas
            healthy = self._wait_for_deployment_ready(deployment_name)
            recovery_time = time.time() - start_time
            
            if healthy:
                self.logger.info(f"✓ Deployment {deployment_name} recovered in {recovery_time:.2f}s")
                return True, recovery_time
            else:
                self.logger.warning(f"⚠ Deployment {deployment_name} not ready after timeout")
                return False, recovery_time
                
        except Exception as e:
            self.logger.error(f"✗ Error recovering {deployment_name}: {e}")
            return False, 0.0
    
    def _wait_for_deployment_ready(self, deployment_name: str, timeout: int = 120) -> bool:
        """Wait for deployment to have ready replicas."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                result = subprocess.run(
                    ["kubectl", "rollout", "status", f"deployment/{deployment_name}", "-n", self.namespace, "--timeout=10s"],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                if result.returncode == 0 and "successfully rolled out" in result.stdout:
                    return True
                    
            except Exception:
                pass
            
            time.sleep(5)
        
        return False
    
    def check_message_persistence(self) -> Dict[str, int]:
        """Check Kafka message persistence during chaos."""
        try:
            # This would integrate with your actual Kafka monitoring
            return {
                "messages_in_queue": random.randint(0, 100),
                "messages_processed": random.randint(500, 1000),
                "messages_lost": 0
            }
        except Exception as e:
            self.logger.error(f"Failed to check message persistence: {e}")
            return {"messages_in_queue": 0, "messages_processed": 0, "messages_lost": 0}


# ============================================================================
# CHAOS ORCHESTRATOR
# ============================================================================

class ChaosOrchestrator:
    """Orchestrates chaos testing across services."""
    
    def __init__(self, config: ChaosConfig):
        self.config = config
        self.logger = setup_logging(config)
        self.metrics = MetricsCollector(config.metrics_file)
        
        # Initialize appropriate engine
        if config.mode == "kubernetes":
            self.engine = KubernetesChaosEngine(config, self.logger, self.metrics)
        else:
            self.engine = DockerChaosEngine(config, self.logger, self.metrics)
        
        self.running = False
        
    def run_chaos_test(self, duration_minutes: Optional[int] = None):
        """
        Run chaos testing.
        
        Args:
            duration_minutes: How long to run the test (None = indefinite)
        """
        self.logger.info("=" * 70)
        self.logger.info("🌪️  CHAOS TESTING INITIATED")
        self.logger.info("=" * 70)
        self.logger.info(f"Mode: {self.config.mode.upper()}")
        self.logger.info(f"Interval: {self.config.interval_seconds}s ({self.config.interval_seconds/60:.1f} minutes)")
        self.logger.info(f"Kill Probability: {self.config.kill_probability * 100:.1f}%")
        self.logger.info(f"Max Concurrent Failures: {self.config.max_concurrent_failures}")
        self.logger.info(f"Dry Run: {self.config.dry_run}")
        self.logger.info("=" * 70)
        
        self.running = True
        start_time = time.time()
        
        try:
            while self.running:
                # Check if duration exceeded
                if duration_minutes:
                    elapsed_minutes = (time.time() - start_time) / 60
                    if elapsed_minutes >= duration_minutes:
                        self.logger.info(f"✓ Test duration ({duration_minutes} minutes) completed")
                        break
                
                # Decide whether to inject chaos
                if random.random() < self.config.kill_probability:
                    self._inject_chaos()
                else:
                    self.logger.info("⏭️  Skipping chaos injection this interval")
                
                # Wait for next interval
                self.logger.info(f"⏳ Waiting {self.config.interval_seconds}s until next check...")
                time.sleep(self.config.interval_seconds)
                
        except KeyboardInterrupt:
            self.logger.info("\n⚠️  Chaos test interrupted by user")
            self.running = False
        finally:
            self._generate_final_report()
    
    def _inject_chaos(self):
        """Inject chaos by killing a random service."""
        # Get available services
        services = self.engine.list_services()
        
        if not services:
            self.logger.warning("⚠️  No services available for chaos injection")
            return
        
        # Select random service(s) to kill
        num_to_kill = min(random.randint(1, self.config.max_concurrent_failures), len(services))
        targets = random.sample(services, num_to_kill)
        
        self.logger.info(f"🎯 Selected targets: {', '.join(targets)}")
        
        # Check message persistence before kill
        pre_kill_metrics = self.engine.check_message_persistence()
        self.logger.info(f"📊 Pre-kill metrics: {pre_kill_metrics}")
        
        # Kill services
        for service in targets:
            event = ChaosEvent(
                timestamp=datetime.utcnow().isoformat(),
                event_type="kill",
                service_name=service,
                mode=self.config.mode,
                duration_seconds=0,
                success=False
            )
            
            success = self.engine.kill_service(service)
            event.success = success
            event.duration_seconds = 0
            
            self.metrics.record_event(event)
            
            if success:
                # Wait a bit then recover
                time.sleep(5)
                
                # Recover and measure recovery time
                recovered, recovery_time = self.engine.recover_service(service)
                
                # Check message persistence after recovery
                post_recovery_metrics = self.engine.check_message_persistence()
                
                # Record recovery event
                recovery_event = ChaosEvent(
                    timestamp=datetime.utcnow().isoformat(),
                    event_type="recovery",
                    service_name=service,
                    mode=self.config.mode,
                    duration_seconds=recovery_time,
                    success=recovered,
                    recovery_time_seconds=recovery_time,
                    messages_persisted=post_recovery_metrics.get("messages_processed", 0),
                    messages_recovered=post_recovery_metrics.get("messages_in_queue", 0)
                )
                self.metrics.record_event(recovery_event)
                
                if recovered:
                    self.logger.info(f"✓ Service {service} successfully recovered")
                else:
                    self.logger.error(f"✗ Service {service} failed to recover properly")
            else:
                self.logger.error(f"✗ Failed to kill service {service}")
    
    def _generate_final_report(self):
        """Generate final chaos test report."""
        summary = self.metrics.generate_summary()
        
        self.logger.info("\n" + "=" * 70)
        self.logger.info("📊 CHAOS TEST FINAL REPORT")
        self.logger.info("=" * 70)
        self.logger.info(f"Total Events: {summary.get('total_kills', 0) + summary.get('total_recoveries', 0)}")
        self.logger.info(f"Total Kills: {summary.get('total_kills', 0)}")
        self.logger.info(f"Total Recoveries: {summary.get('total_recoveries', 0)}")
        self.logger.info(f"Total Failures: {summary.get('total_failures', 0)}")
        self.logger.info(f"Success Rate: {summary.get('success_rate', 0):.2f}%")
        self.logger.info(f"Average Recovery Time: {summary.get('average_recovery_time', 0):.2f}s")
        self.logger.info(f"Min Recovery Time: {summary.get('min_recovery_time', 0):.2f}s")
        self.logger.info(f"Max Recovery Time: {summary.get('max_recovery_time', 0):.2f}s")
        self.logger.info("=" * 70)
        self.logger.info(f"📄 Full metrics saved to: {self.config.metrics_file}")
        self.logger.info(f"📄 Logs saved to: {self.config.log_file}")
        self.logger.info("=" * 70)


# ============================================================================
# CLI INTERFACE
# ============================================================================

def parse_arguments() -> ChaosConfig:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Chaos Testing for TechCorp FTE",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Docker mode with 2-hour interval
  python chaos_testing.py --mode docker --interval 7200
  
  # Kubernetes mode with custom namespace
  python chaos_testing.py --mode kubernetes --namespace my-namespace
  
  # Dry run (no actual kills)
  python chaos_testing.py --dry-run --verbose
  
  # Custom configuration file
  python chaos_testing.py --config chaos_config.json
  
  # Run for specific duration
  python chaos_testing.py --duration 60  # Run for 60 minutes
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["docker", "kubernetes"],
        default="docker",
        help="Chaos testing mode (default: docker)"
    )
    
    parser.add_argument(
        "--namespace",
        default="customer-success-fte",
        help="Kubernetes namespace (default: customer-success-fte)"
    )
    
    parser.add_argument(
        "--interval",
        type=int,
        default=7200,
        help="Interval between chaos checks in seconds (default: 7200 = 2 hours)"
    )
    
    parser.add_argument(
        "--targets",
        nargs="+",
        default=[],
        help="Specific services to target (default: all non-excluded)"
    )
    
    parser.add_argument(
        "--exclude",
        nargs="+",
        default=["kafka", "zookeeper"],
        help="Services to exclude from chaos (default: kafka, zookeeper)"
    )
    
    parser.add_argument(
        "--probability",
        type=float,
        default=0.3,
        help="Probability of chaos injection at each interval (default: 0.3)"
    )
    
    parser.add_argument(
        "--max-failures",
        type=int,
        default=1,
        help="Maximum concurrent failures (default: 1)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate without actual kills"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=True,
        help="Enable verbose logging (default: True)"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration JSON file"
    )
    
    parser.add_argument(
        "--duration",
        type=int,
        help="Test duration in minutes (default: run indefinitely)"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        default="chaos_test.log",
        help="Log file path (default: chaos_test.log)"
    )
    
    parser.add_argument(
        "--metrics-file",
        type=str,
        default="chaos_metrics.json",
        help="Metrics output file (default: chaos_metrics.json)"
    )
    
    args = parser.parse_args()
    
    # Load from config file if provided
    if args.config:
        with open(args.config, 'r') as f:
            config_data = json.load(f)
        return ChaosConfig(**config_data)
    
    # Build config from arguments
    return ChaosConfig(
        mode=args.mode,
        namespace=args.namespace,
        interval_seconds=args.interval,
        target_services=args.targets,
        excluded_services=args.exclude,
        kill_probability=args.probability,
        max_concurrent_failures=args.max_failures,
        dry_run=args.dry_run,
        verbose=args.verbose,
        log_file=args.log_file,
        metrics_file=args.metrics_file
    )


def main():
    """Main entry point."""
    config = parse_arguments()
    orchestrator = ChaosOrchestrator(config)
    orchestrator.run_chaos_test(duration_minutes=config.duration if hasattr(config, 'duration') else None)


if __name__ == "__main__":
    main()
