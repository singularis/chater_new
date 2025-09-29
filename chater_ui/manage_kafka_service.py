#!/usr/bin/env python3
import argparse
import logging
import os
import signal
import sys
import time

from kafka_consumer_service import (kafka_service,
                                    start_kafka_consumer_service,
                                    stop_kafka_consumer_service)
from logging_config import setup_logging

setup_logging("kafka_service_manager.log")
logger = logging.getLogger("kafka_service_manager")


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}, shutting down...")
    stop_kafka_consumer_service()
    sys.exit(0)


def run_service():
    """Run the Kafka consumer service standalone"""
    logger.info("Starting standalone Kafka Consumer Service...")

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        start_kafka_consumer_service()
        logger.info("Kafka Consumer Service is running. Press Ctrl+C to stop.")

        # Keep the service running
        while kafka_service.is_running:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Error running service: {e}")
    finally:
        stop_kafka_consumer_service()
        logger.info("Service stopped")


def check_status():
    """Check if the service is running"""
    if kafka_service.is_running:
        print("Kafka Consumer Service is RUNNING")
        print(f"Active threads: {len(kafka_service.threads)}")
        return True
    else:
        print("Kafka Consumer Service is STOPPED")
        return False


def main():
    parser = argparse.ArgumentParser(description="Manage Kafka Consumer Service")
    parser.add_argument(
        "action", choices=["start", "stop", "status", "run"], help="Action to perform"
    )

    args = parser.parse_args()

    if args.action == "start":
        if kafka_service.is_running:
            print("Service is already running")
        else:
            start_kafka_consumer_service()
            print("Service started")

    elif args.action == "stop":
        if not kafka_service.is_running:
            print("Service is not running")
        else:
            stop_kafka_consumer_service()
            print("Service stopped")

    elif args.action == "status":
        check_status()

    elif args.action == "run":
        run_service()


if __name__ == "__main__":
    main()
