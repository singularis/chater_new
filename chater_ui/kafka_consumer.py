import json
import logging
import os
import time
from typing import List

from confluent_kafka import Consumer, KafkaError, KafkaException, Message
from logging_config import setup_logging

setup_logging("kafka_consumer.log")
logger = logging.getLogger(__name__)


def create_consumer(
    user_email: str,
    topics: List[str],
    offset_reset: str = "latest",
    enable_auto_commit: bool = False,
    max_poll_interval_ms: int = 300000,
):
    """
    Create a Kafka consumer with user-specific configuration.
    
    Args:
        user_email: Email of the user for the consumer group
        topics: List of topics to subscribe to
        offset_reset: Where to start reading messages ('earliest' or 'latest')
        enable_auto_commit: Whether to automatically commit offsets
        max_poll_interval_ms: Maximum time between polls before consumer is considered dead
        
    Returns:
        Configured Kafka consumer instance
    """
    try:
        # Use user email as part of group ID for user-specific consumption
        group_id = f"chater-ui-{user_email}"
        
        conf = {
            "bootstrap.servers": os.getenv("BOOTSTRAP_SERVER"),
            "group.id": group_id,
            "auto.offset.reset": offset_reset,
            "enable.auto.commit": str(enable_auto_commit).lower(),
            "max.poll.interval.ms": max_poll_interval_ms,
            # Performance optimizations for confluent-kafka
            "queued.min.messages": 10000,  # Pre-fetch messages for performance
            "session.timeout.ms": 30000,
            "heartbeat.interval.ms": 10000,
        }
        
        consumer = Consumer(conf)
        logger.info(f"Consumer created for user {user_email} with group {group_id}")
        
        # Subscribe to topics with rebalance callbacks
        def on_assign(consumer, partitions):
            logger.info(f"Partitions assigned: {partitions}")
            
        def on_revoke(consumer, partitions):
            logger.info(f"Partitions revoked: {partitions}")
            
        consumer.subscribe(topics, on_assign=on_assign, on_revoke=on_revoke)
        logger.info(f"Subscribed to topics: {topics}")
        
        return consumer
        
    except KafkaException as e:
        logger.error(f"Failed to create consumer: {str(e)}")
        raise


def consume_messages(consumer: Consumer, user_email: str, batch_size: int = 1):
    """
    Consume messages from Kafka for a specific user with optional batching.
    
    Args:
        consumer: Kafka consumer instance
        user_email: Email of the user to filter messages for
        batch_size: Number of messages to batch before yielding (1 for no batching)
        
    Yields:
        List of messages (or single message if batch_size=1) belonging to the user
    """
    logger.info(f"Starting message consumption for user {user_email} with batch size {batch_size}")
    
    message_batch = []
    last_batch_time = time.time()
    batch_timeout = 5.0  # seconds
    
    while True:
        try:
            msg = consumer.poll(timeout=0.1)  # Reduced timeout for responsiveness
            
            if msg is None:
                # Check if we should yield partial batch due to timeout
                if message_batch and (time.time() - last_batch_time) > batch_timeout:
                    if batch_size == 1:
                        yield message_batch[0]
                    else:
                        yield message_batch
                    message_batch = []
                    last_batch_time = time.time()
                continue
                
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.debug(f"End of partition reached for topic {msg.topic()}")
                    continue
                else:
                    logger.error(f"Consumer error: {msg.error()}")
                    continue
                    
            # Parse and validate message
            try:
                message_value = msg.value().decode("utf-8")
                message_data = json.loads(message_value)
                
                # Check if message belongs to the user
                msg_user_email = None
                if isinstance(message_data, dict):
                    # Check for user_email in different locations
                    if "user_email" in message_data:
                        msg_user_email = message_data["user_email"]
                    elif "value" in message_data and isinstance(message_data["value"], dict):
                        msg_user_email = message_data["value"].get("user_email")
                        
                if msg_user_email != user_email:
                    logger.debug(f"Skipping message for different user: {msg_user_email}")
                    # Commit skipped messages if auto-commit is disabled
                    if not consumer._conf.get("enable.auto.commit", "false") == "true":
                        consumer.commit(message=msg)
                    continue
                    
                logger.info(f"Message received for user {user_email}: {msg.key()}")
                
                # Add to batch
                message_batch.append(msg)
                
                # Yield if batch is full
                if len(message_batch) >= batch_size:
                    if batch_size == 1:
                        yield message_batch[0]
                    else:
                        yield message_batch
                    message_batch = []
                    last_batch_time = time.time()
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse message as JSON: {str(e)}")
                # Commit invalid messages
                if not consumer._conf.get("enable.auto.commit", "false") == "true":
                    consumer.commit(message=msg)
                continue
                
        except Exception as e:
            logger.error(f"Unexpected error in consume loop: {str(e)}")
            continue


def commit_messages(consumer: Consumer, messages: List[Message]):
    """
    Commit offsets for a batch of messages.
    
    Args:
        consumer: Kafka consumer instance
        messages: List of messages to commit
    """
    try:
        if messages:
            # Commit the offset of the last message + 1
            last_msg = messages[-1]
            consumer.commit(message=last_msg)
            logger.debug(f"Committed {len(messages)} messages")
    except KafkaException as e:
        logger.error(f"Failed to commit messages: {str(e)}")
        raise


def consume_messages_with_timeout(
    consumer: Consumer,
    user_email: str,
    timeout_seconds: float,
    batch_size: int = 1
):
    """
    Consume messages with a timeout, useful for request-response patterns.
    
    Args:
        consumer: Kafka consumer instance
        user_email: Email of the user to filter messages for
        timeout_seconds: Maximum time to wait for messages
        batch_size: Number of messages to batch
        
    Yields:
        Messages received within the timeout period
    """
    start_time = time.time()
    
    for messages in consume_messages(consumer, user_email, batch_size):
        yield messages
        
        if time.time() - start_time > timeout_seconds:
            logger.info(f"Timeout reached after {timeout_seconds} seconds")
            break


def close_consumer(consumer: Consumer):
    """Properly close the consumer"""
    try:
        consumer.close()
        logger.info("Consumer closed successfully")
    except Exception as e:
        logger.error(f"Error closing consumer: {str(e)}")
