import logging
import os

from confluent_kafka import Consumer, KafkaError, KafkaException

from logging_config import setup_logging

setup_logging("kafka_consumer.log")
logger = logging.getLogger("kafka_consumer")


def create_consumer(topics):
    if not isinstance(topics, list):
        logger.error("Expected list of topic unicode strings")
        raise TypeError("Expected list of topic unicode strings")

    try:
        consumer = Consumer(
            {
                "bootstrap.servers": os.getenv("BOOTSTRAP_SERVER"),
                "group.id": "chater",
                "auto.offset.reset": "earliest",
                "enable.auto.commit": True,
            }
        )

        def on_assign(consumer, partitions):
            logger.info(f"Assigned partitions: {partitions}")

        consumer.subscribe(topics, on_assign=on_assign)
        logger.info(f"Subscribed to topics: {topics}")
        return consumer
    except KafkaException as e:
        logger.error(f"Failed to create consumer: {str(e)}")
        raise


def consume_messages(consumer):
    try:
        while True:
            msg = consumer.poll(2.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.info(f"End of partition reached {msg.partition()}")
                    continue
                else:
                    logger.error(f"Consumer error: {msg.error()}")
                    continue

            logger.info(f"Consumed message: {msg.key()} - {msg.value()}")
            yield msg
    except KafkaException as e:
        logger.error(f"Error while consuming messages: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise
    finally:
        consumer.close()
        logger.info("Consumer closed")
