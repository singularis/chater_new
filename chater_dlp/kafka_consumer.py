import logging
import os

from confluent_kafka import Consumer, KafkaError

logger = logging.getLogger("kafka_consumer")


def consume_messages(topics, batch_size=1):
    logger.info(f"Starting Kafka consumer with topics: {topics}")
    if not isinstance(topics, list):
        logger.error("Expected list of topic unicode strings")
        raise TypeError("Expected list of topic unicode strings")

    consumer = Consumer(
        {
            "bootstrap.servers": os.getenv("BOOTSTRAP_SERVER"),
            "group.id": "dlp",
            "auto.offset.reset": "latest",
            "enable.auto.commit": False,
            # Performance optimizations for confluent-kafka
            "queued.min.messages": 10000,  # Pre-fetch messages for performance
            "session.timeout.ms": 30000,
            "heartbeat.interval.ms": 10000,
        }
    )

    consumer.subscribe(topics)
    
    message_batch = []

    while True:
        msg = consumer.poll(0.1)  # Reduced poll timeout
        if msg is None:
            # Yield partial batch if exists
            if message_batch:
                if batch_size == 1:
                    yield message_batch[0], consumer
                else:
                    yield message_batch, consumer
                message_batch = []
            continue
            
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                logger.debug(f"End of partition reached")
                continue
            else:
                logger.error(f"Consumer error: {msg.error()}")
                continue

        logger.debug(f"Consumed message: {msg}")
        message_batch.append(msg)
        
        # Yield batch if full
        if len(message_batch) >= batch_size:
            if batch_size == 1:
                yield message_batch[0], consumer
            else:
                yield message_batch, consumer
            message_batch = []


def commit_batch(consumer, messages):
    """Commit offsets for a batch of messages"""
    if messages:
        # Commit the last message offset
        last_msg = messages[-1] if isinstance(messages, list) else messages
        consumer.commit(message=last_msg)
        logger.debug(f"Committed batch of {len(messages) if isinstance(messages, list) else 1} messages")
