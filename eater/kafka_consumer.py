import json
import logging
import os
from datetime import time

from confluent_kafka import Consumer, KafkaError, KafkaException

logger = logging.getLogger("kafka_consumer")


def validate_user_data(message_data, expected_user_email=None):
    """Validate that the message belongs to the expected user."""
    try:
        # If message_data is a string, try to parse it as JSON
        if isinstance(message_data, str):
            try:
                message_data = json.loads(message_data)
            except json.JSONDecodeError:
                logger.error("Failed to parse message as JSON")
                return False

        # Handle different message structures
        if isinstance(message_data, dict):
            # Get user_email from different possible locations
            message_user_email = None

            # Check root level
            if "user_email" in message_data:
                message_user_email = message_data.get("user_email")
            # Check value object
            elif "value" in message_data:
                value_obj = message_data.get("value", {})
                if isinstance(value_obj, dict):
                    message_user_email = value_obj.get("user_email")
                elif isinstance(value_obj, str):
                    try:
                        value_dict = json.loads(value_obj)
                        message_user_email = value_dict.get("user_email")
                    except json.JSONDecodeError:
                        pass

            if not message_user_email:
                logger.warning("No user_email found in message")
                return False

            if expected_user_email and message_user_email != expected_user_email:
                logger.warning(
                    f"User email mismatch. Expected: {expected_user_email}, Got: {message_user_email}"
                )
                return False

            return True
        else:
            logger.error(f"Unexpected message format: {type(message_data)}")
            return False
    except Exception as e:
        logger.error(f"Error validating user data: {str(e)}")
        return False


def consume_messages(topics, expected_user_email=None):
    logger.info(
        f"Starting Kafka consumer with topics: {topics} for user: {expected_user_email}"
    )
    if not isinstance(topics, list):
        logger.error("Expected list of topic unicode strings")
        raise TypeError("Expected list of topic unicode strings")

    consumer = Consumer(
        {
            "bootstrap.servers": os.getenv("BOOTSTRAP_SERVER"),
            "group.id": "eater",
            "auto.offset.reset": "latest",
            "enable.auto.commit": False,
            "max.poll.interval.ms": 300000,
            # Performance optimizations for confluent-kafka
            "queued.min.messages": 10000,  # Pre-fetch messages for performance
            "session.timeout.ms": 30000,  # 30 seconds
            "heartbeat.interval.ms": 10000,  # 10 seconds
        }
    )

    consumer.subscribe(topics)
    
    # Batch processing variables
    batch_size = 100
    batch_timeout = 5.0  # seconds
    message_batch = []

    while True:
        msg = consumer.poll(0.1)  # Reduced poll timeout for better responsiveness
        if msg is None:
            # If we have messages in batch and timeout reached, yield them
            if message_batch:
                yield message_batch, consumer
                message_batch = []
            continue
            
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                logger.debug(f"End of partition reached for topic {msg.topic()}")
                continue
            elif msg.error().code() == KafkaError.BROKER_NOT_AVAILABLE:
                logger.error("Broker not available. Retrying in 5 seconds...")
                time.sleep(5)
                continue
            elif msg.error().code() == KafkaError.INVALID_MSG_SIZE:
                logger.error(f"Message too large: {msg.error()}")
                continue
            else:
                logger.error(f"Consumer error: {msg.error()}")
                continue

        try:
            message_data = json.loads(msg.value())
            logger.debug(f"Received message: {message_data}")
            if not validate_user_data(message_data, expected_user_email):
                logger.warning(f"Skipping message for unexpected user: {message_data}")
                consumer.commit(message=msg)  # Commit skipped messages
                continue

            user_email = message_data.get("value", {}).get("user_email", "unknown")
            logger.info(
                f"Consumed message for user {user_email}: {msg.key()} - {msg.value()}"
            )
            
            # Add to batch
            message_batch.append(msg)
            
            # Yield batch if size reached
            if len(message_batch) >= batch_size:
                yield message_batch, consumer
                message_batch = []
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message as JSON: {str(e)}")
            consumer.commit(message=msg)  # Commit invalid messages
            continue
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            continue


def consume_messages_single(topics, expected_user_email=None):
    """Legacy single message consumption for compatibility"""
    for batch, consumer in consume_messages(topics, expected_user_email):
        for msg in batch:
            yield msg, consumer
