import logging
import os

from confluent_kafka import Consumer, KafkaError

logger = logging.getLogger("kafka_consumer")


class NoMessageError(Exception):
    pass


def consume_messages(
    topics,
):
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

    while True:
        msg = consumer.poll(2.0)
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
