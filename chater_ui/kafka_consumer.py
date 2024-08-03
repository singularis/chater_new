from confluent_kafka import Consumer, KafkaError
import logging
import os

logger = logging.getLogger("kafka_consumer")


def create_consumer(topics):
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
    return consumer


def consume_messages(consumer):
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                logger.error(f"Consumer error: {msg.error()}")
                continue

        logger.info(f"Consumed message: {msg.key()} - {msg.value()}")
        yield msg
