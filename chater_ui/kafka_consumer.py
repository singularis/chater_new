import json
import logging
import os
import time
from typing import Generator, List, Optional

from confluent_kafka import Consumer, KafkaError, KafkaException, Message
from logging_config import setup_logging

setup_logging("kafka_consumer.log")
logger = logging.getLogger("kafka_consumer")


def create_consumer(topics: List[str]) -> Consumer:
    """
    Create a Kafka consumer with essential configurations.
    
    Args:
        topics: List of topic names to subscribe to
        
    Returns:
        Configured Kafka consumer instance
        
    Raises:
        TypeError: If topics is not a list
        KafkaException: If consumer creation fails
    """
    if not isinstance(topics, list):
        logger.error("Expected list of topic unicode strings")
        raise TypeError("Expected list of topic unicode strings")

    # Essential configuration only
    config = {
        "bootstrap.servers": os.getenv("BOOTSTRAP_SERVER", "localhost:9092"),
        "group.id": f"chater-{int(time.time())}",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
        "auto.commit.interval.ms": 5000,
        "session.timeout.ms": 30000,
        "heartbeat.interval.ms": 10000,
        "max.poll.interval.ms": 300000,
    }

    try:
        consumer = Consumer(config)

        def on_assign(consumer_instance, partitions):
            partition_info = [f"{p.topic}:{p.partition}" for p in partitions]
            logger.info(f"Assigned partitions: {partition_info}")

        def on_revoke(consumer_instance, partitions):
            partition_info = [f"{p.topic}:{p.partition}" for p in partitions]
            logger.info(f"Partitions revoked: {partition_info}")

        consumer.subscribe(topics, on_assign=on_assign, on_revoke=on_revoke)
        logger.info(f"Successfully subscribed to topics: {topics}")
        return consumer
        
    except KafkaException as e:
        logger.error(f"Failed to create consumer: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating consumer: {str(e)}")
        raise


def consume_messages(consumer: Consumer, expected_user_email: Optional[str] = None) -> Generator[Message, None, None]:
    consecutive_errors = 0
    max_consecutive_errors = 5
    
    try:
        logger.info("Starting message consumption...")
        
        while True:
            try:
                msg = consumer.poll(timeout=1.0)
                
                if msg is None:
                    consecutive_errors = 0
                    continue
                
                if msg.error():
                    error_code = msg.error().code()
                    
                    if error_code == KafkaError._PARTITION_EOF:
                        logger.debug(f"End of partition reached for topic {msg.topic()}")
                        consecutive_errors = 0
                        continue
                        
                    elif error_code == KafkaError.BROKER_NOT_AVAILABLE:
                        consecutive_errors += 1
                        logger.warning(f"Broker not available (attempt {consecutive_errors})")
                        if consecutive_errors < max_consecutive_errors:
                            time.sleep(min(consecutive_errors, 5))
                            continue
                        else:
                            logger.error("Broker unavailable for too long, stopping consumer")
                            break
                            
                    elif error_code == KafkaError.INVALID_MSG_SIZE:
                        logger.error(f"Message too large, skipping: {msg.error()}")
                        consecutive_errors = 0
                        continue
                        
                    else:
                        consecutive_errors += 1
                        logger.error(f"Consumer error (attempt {consecutive_errors}): {msg.error()}")
                        if consecutive_errors >= max_consecutive_errors:
                            logger.error("Too many consecutive errors, stopping consumer")
                            break
                        time.sleep(1)
                        continue

                consecutive_errors = 0
                
                try:
                    message_data = json.loads(msg.value().decode('utf-8'))
                    value = message_data.get("value", {})
                    user_email = (
                        value.get("user_email", "unknown")
                        if isinstance(value, dict)
                        else "unknown"
                    )
                    
                    logger.info(
                        f"Consumed message for user {user_email}: "
                        f"key={msg.key()}, topic={msg.topic()}, offset={msg.offset()}"
                    )
                    
                    yield msg
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse message as JSON: {str(e)}")
                    continue
                except UnicodeDecodeError as e:
                    logger.error(f"Failed to decode message: {str(e)}")
                    continue
                except Exception as e:
                    logger.error(f"Unexpected error processing message: {str(e)}")
                    continue

            except KafkaException as e:
                consecutive_errors += 1
                logger.error(f"Kafka exception during polling (attempt {consecutive_errors}): {str(e)}")
                if consecutive_errors >= max_consecutive_errors:
                    logger.error("Too many consecutive Kafka errors, stopping consumer")
                    break
                time.sleep(min(consecutive_errors, 5))
                
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Unexpected error during consumption (attempt {consecutive_errors}): {str(e)}")
                if consecutive_errors >= max_consecutive_errors:
                    logger.error("Too many consecutive unexpected errors, stopping consumer")
                    break
                time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down gracefully...")
    except Exception as e:
        logger.error(f"Fatal error in message consumption: {str(e)}")
        raise
    finally:
        logger.info("Shutting down consumer...")
        try:
            consumer.close()
            logger.info("Consumer closed successfully")
        except Exception as e:
            logger.warning(f"Error closing consumer: {e}")


def consume_messages_with_timeout(consumer: Consumer, timeout_seconds: int = 30, expected_user_email: Optional[str] = None) -> Generator[Message, None, None]:
    """
    Consume messages with a timeout - designed for request-response patterns.
    
    Args:
        consumer: Kafka consumer instance
        timeout_seconds: Maximum time to wait for messages before timing out
        expected_user_email: Optional user email filter
        
    Yields:
        Message: Kafka messages received within the timeout period
    """
    start_time = time.time()
    consecutive_errors = 0
    max_consecutive_errors = 5
    
    try:
        logger.info(f"Starting message consumption with {timeout_seconds}s timeout...")
        
        while time.time() - start_time < timeout_seconds:
            try:
                msg = consumer.poll(timeout=1.0)
                
                if msg is None:
                    consecutive_errors = 0
                    continue
                
                if msg.error():
                    error_code = msg.error().code()
                    
                    if error_code == KafkaError._PARTITION_EOF:
                        logger.debug(f"End of partition reached for topic {msg.topic()}")
                        consecutive_errors = 0
                        continue
                        
                    elif error_code == KafkaError.BROKER_NOT_AVAILABLE:
                        consecutive_errors += 1
                        logger.warning(f"Broker not available (attempt {consecutive_errors})")
                        if consecutive_errors < max_consecutive_errors:
                            time.sleep(min(consecutive_errors, 5))
                            continue
                        else:
                            logger.error("Broker unavailable for too long, stopping consumer")
                            break
                            
                    elif error_code == KafkaError.INVALID_MSG_SIZE:
                        logger.error(f"Message too large, skipping: {msg.error()}")
                        consecutive_errors = 0
                        continue
                        
                    else:
                        consecutive_errors += 1
                        logger.error(f"Consumer error (attempt {consecutive_errors}): {msg.error()}")
                        if consecutive_errors >= max_consecutive_errors:
                            logger.error("Too many consecutive errors, stopping consumer")
                            break
                        time.sleep(1)
                        continue

                consecutive_errors = 0
                
                try:
                    message_data = json.loads(msg.value().decode('utf-8'))
                    value = message_data.get("value", {})
                    user_email = (
                        value.get("user_email", "unknown")
                        if isinstance(value, dict)
                        else "unknown"
                    )
                    
                    # Filter by user email if specified
                    if expected_user_email and user_email != expected_user_email:
                        logger.debug(f"Skipping message for different user: {user_email}")
                        continue
                    
                    logger.info(
                        f"Consumed message for user {user_email}: "
                        f"key={msg.key()}, topic={msg.topic()}, offset={msg.offset()}"
                    )
                    
                    yield msg
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse message as JSON: {str(e)}")
                    continue
                except UnicodeDecodeError as e:
                    logger.error(f"Failed to decode message: {str(e)}")
                    continue
                except Exception as e:
                    logger.error(f"Unexpected error processing message: {str(e)}")
                    continue

            except KafkaException as e:
                consecutive_errors += 1
                logger.error(f"Kafka exception during polling (attempt {consecutive_errors}): {str(e)}")
                if consecutive_errors >= max_consecutive_errors:
                    logger.error("Too many consecutive Kafka errors, stopping consumer")
                    break
                time.sleep(min(consecutive_errors, 5))
                
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Unexpected error during consumption (attempt {consecutive_errors}): {str(e)}")
                if consecutive_errors >= max_consecutive_errors:
                    logger.error("Too many consecutive unexpected errors, stopping consumer")
                    break
                time.sleep(1)
        
        logger.info(f"Message consumption timeout reached after {timeout_seconds}s")

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down gracefully...")
    except Exception as e:
        logger.error(f"Fatal error in message consumption: {str(e)}")
        raise
