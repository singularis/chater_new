import logging
import os
import time
from confluent_kafka import Consumer, KafkaError

logger = logging.getLogger("kafka_consumer")

class NoMessageError(Exception):
    pass

def consume_messages(topics,):
    logger.info(f"Starting Kafka consumer with topics: {topics}")
    if not isinstance(topics, list):
        logger.error("Expected list of topic unicode strings")
        raise TypeError("Expected list of topic unicode strings")

    consumer = Consumer(
        {
            "bootstrap.servers": os.getenv("BOOTSTRAP_SERVER"),
            "group.id": "chater",
            "auto.offset.reset": "latest",
            "enable.auto.commit": False,
        }
    )

    consumer.subscribe(topics)
    start_time = time.time()
    timeout = os.getenv("timeout")

    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > int(timeout):
            logger.error("No messages received in 60 seconds")
            raise NoMessageError("No messages received in 60 seconds")

        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                logger.error(f"Consumer error: {msg.error()}")
                continue

        logger.info(f"Consumed message: {msg}")
        yield msg, consumer
        start_time = time.time()
