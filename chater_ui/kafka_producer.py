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
        message_data = json.loads(msg.value())
        user_email = message_data.get("value", {}).get("user_email", "unknown")
        logger.info(
            f"Message delivered to {msg.topic()} [{msg.partition()}] for user {user_email}"
        )


def produce_message(producer, topic, message):
    try:
        # Ensure message has a value field
        if "value" not in message:
            message["value"] = {}

        # Debug logging for auth topic
        if topic == "auth_requires_token":
            logger.info(f"AUTH DEBUG - Message before user_email check: {message}")
            logger.info(f"AUTH DEBUG - Message value keys: {list(message.get('value', {}).keys())}")
            logger.info(f"AUTH DEBUG - user_email in value: {'user_email' in message.get('value', {})}")

        # Add user_email to the message if not present
        if "user_email" not in message["value"]:
            logger.warning(f"No user_email found in message value for topic {topic}")
            logger.warning(f"Message structure: {message}")
            message["value"]["user_email"] = "unknown"

        producer.produce(
            topic,
            key=message.get("key"),
            value=json.dumps(message),
            callback=delivery_report,
        )
        producer.flush()
        logger.info(
            f"Message produced to topic {topic} for user {message['value']['user_email']}"
        )
    except KafkaException as e:
        logger.error(f"Failed to produce message: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise
