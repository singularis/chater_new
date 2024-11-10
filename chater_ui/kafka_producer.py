import json
import logging
import os

from confluent_kafka import KafkaException, Producer

from logging_config import setup_logging

setup_logging("kafka_producer.log")
logger = logging.getLogger(__name__)


def create_producer():
    try:
        conf = {
            "bootstrap.servers": os.getenv("BOOTSTRAP_SERVER"),
            "message.max.bytes": 10000000,
            "client.id": "python-producer",
            "acks": "all",
        }
        producer = Producer(conf)
        logger.info("Producer created successfully")
        return producer
    except KafkaException as e:
        logger.error(f"Failed to create producer: {str(e)}")
        raise


def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def produce_message(producer, topic, message):
    try:
        producer.produce(
            topic,
            key=message.get("key"),
            value=json.dumps(message),
            callback=delivery_report,
        )
        producer.flush()
        logger.info(f"Message produced to topic {topic}")
    except KafkaException as e:
        logger.error(f"Failed to produce message: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise
