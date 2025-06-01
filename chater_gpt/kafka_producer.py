import json
import logging
import os

from confluent_kafka import Producer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

conf = {
    "bootstrap.servers": os.getenv("BOOTSTRAP_SERVER"),
    "message.max.bytes": 10000000,
    "client.id": "python-gpt-producer",
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

producer = Producer(conf)


def delivery_report(err, msg):
    if err is not None:
        logger.error("Message delivery failed: {}".format(err))
    else:
        logger.debug("Message delivered to {} [{}]".format(msg.topic(), msg.partition()))


def produce_message(topic, message):
    try:
        producer.produce(
            topic,
            key=(message["key"]),
            value=json.dumps(message),
            callback=delivery_report,
        )
        # Don't flush immediately - let batching work
        producer.poll(0)  # Trigger callbacks without blocking
    except BufferError:
        # Handle queue full
        logger.warning("Producer queue full, waiting...")
        producer.flush(timeout=10)
        # Retry
        producer.produce(
            topic,
            key=(message["key"]),
            value=json.dumps(message),
            callback=delivery_report,
        )
    except Exception as e:
        logger.error("Failed to produce message: {}".format(e))
        raise


def flush_producer(timeout=30):
    """Flush any pending messages"""
    producer.flush(timeout)
