import json
import logging
import os
import threading
import time

from confluent_kafka import KafkaException, Producer
from logging_config import setup_logging

setup_logging("kafka_producer.log")
logger = logging.getLogger(__name__)

# Global producer instance for reuse
_producer = None
_producer_lock = threading.Lock()


def create_producer():
    global _producer
    with _producer_lock:
        if _producer is None:
            try:
                conf = {
                    "bootstrap.servers": os.getenv("BOOTSTRAP_SERVER"),
                    "message.max.bytes": 10000000,
                    "client.id": "python-ui-producer",
                    "acks": "all",
                    # Performance optimizations - using correct Python property names
                    "compression.type": "lz4",
                    "batch.num.messages": 200,  # Batch up to 200 messages
                    "queue.buffering.max.messages": 200000,  # Queue up to 200K messages
                    "queue.buffering.max.kbytes": 131072,  # 128MB buffer
                    "queue.buffering.max.ms": 20,  # Wait up to 20ms for batching
                    "enable.idempotence": True,
                    "retries": 5,
                    "retry.backoff.ms": 100,
                    "max.in.flight.requests.per.connection": 5,
                    "message.send.max.retries": 5,
                    "request.timeout.ms": 30000,  # 30 seconds
                }
                _producer = Producer(conf)
                logger.info("Producer created successfully")
                
                # Start background thread for polling
                poll_thread = threading.Thread(target=_poll_loop, daemon=True)
                poll_thread.start()
                
            except KafkaException as e:
                logger.error(f"Failed to create producer: {str(e)}")
                raise
        return _producer


def _poll_loop():
    """Background thread to poll for delivery reports"""
    while True:
        if _producer:
            _producer.poll(0.1)
        time.sleep(0.1)


def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        try:
            message_data = json.loads(msg.value())
            user_email = message_data.get("value", {}).get("user_email", "unknown")
            logger.debug(
                f"Message delivered to {msg.topic()} [{msg.partition()}] for user {user_email}"
            )
        except:
            logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def produce_message(producer, topic, message):
    if producer is None:
        producer = create_producer()
        
    try:
        # Ensure message has a value field
        if "value" not in message:
            message["value"] = {}

        # Add user_email to the message if not present
        if "user_email" not in message["value"]:
            logger.warning("No user_email found in message value")
            message["value"]["user_email"] = "unknown"

        # Produce without blocking
        producer.produce(
            topic,
            key=message.get("key"),
            value=json.dumps(message),
            callback=delivery_report,
        )
        
        logger.info(
            f"Message queued for topic {topic} for user {message['value']['user_email']}"
        )
    except BufferError as e:
        logger.warning(f"Producer buffer full, flushing: {str(e)}")
        producer.flush(timeout=10)
        # Retry after flush
        producer.produce(
            topic,
            key=message.get("key"),
            value=json.dumps(message),
            callback=delivery_report,
        )
    except KafkaException as e:
        logger.error(f"Failed to produce message: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise


def flush_all(timeout=30):
    """Flush all pending messages"""
    if _producer:
        _producer.flush(timeout)
