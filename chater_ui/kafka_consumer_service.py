import json
import logging
import os
import threading
import time
from datetime import datetime

import redis
from confluent_kafka import Consumer, KafkaError, KafkaException
from logging_config import setup_logging

setup_logging("kafka_consumer_service.log")
logger = logging.getLogger("kafka_consumer_service")


class KafkaConsumerService:
    def __init__(self):
        self.redis_client = redis.StrictRedis(
            host=os.getenv("REDIS_ENDPOINT"), port=6379, db=0
        )
        self.consumers = {}
        self.is_running = False
        self.threads = []
        
        # Topics to consume from based on target configurations
        self.topic_configs = {
            "gpt-response": {"name": "gpt-response"},
            "gemini-response": {"name": "gemini-response"},
            "send_today_data": {"name": "send_today_data"},
            "photo-analysis-response-check": {"name": "photo-analysis-response-check"},
            "delete_food_response": {"name": "delete_food_response"},
        }

    def create_consumer(self, topics):
        """Create a Kafka consumer for specific topics"""
        if not isinstance(topics, list):
            logger.error("Expected list of topic unicode strings")
            raise TypeError("Expected list of topic unicode strings")

        try:
            consumer = Consumer(
                {
                    "bootstrap.servers": os.getenv("BOOTSTRAP_SERVER"),
                    "group.id": "chater_background_service",
                    "auto.offset.reset": "earliest",
                    "enable.auto.commit": True,
                    "max.poll.interval.ms": 300000,
                    "session.timeout.ms": 30000,
                    "heartbeat.interval.ms": 10000,
                }
            )

            def on_assign(consumer, partitions):
                logger.info(f"Assigned partitions: {partitions}")

            def on_revoke(consumer, partitions):
                logger.info(f"Partitions revoked: {partitions}")

            consumer.subscribe(topics, on_assign=on_assign, on_revoke=on_revoke)
            logger.info(f"Subscribed to topics: {topics}")
            return consumer
        except KafkaException as e:
            logger.error(f"Failed to create consumer: {str(e)}")
            raise

    def store_response_in_redis(self, message_uuid, response_data, user_email=None):
        """Store response in Redis with expiration"""
        try:
            # Store response for 10 minutes (600 seconds)
            self.redis_client.setex(
                f"kafka_response:{message_uuid}", 
                600, 
                json.dumps(response_data)
            )
            
            # Also store with user-specific key if user_email is provided
            if user_email:
                self.redis_client.setex(
                    f"kafka_response_user:{user_email}:{message_uuid}", 
                    600, 
                    json.dumps(response_data)
                )
            
            logger.info(f"Stored response for message UUID: {message_uuid}" + 
                       (f" and user: {user_email}" if user_email else ""))
        except Exception as e:
            logger.error(f"Failed to store response in Redis: {str(e)}")

    def consume_topic_messages(self, topics):
        """Consume messages from specific topics continuously"""
        consumer = self.create_consumer(topics)
        logger.info(f"Starting consumer for topics: {topics}")
        
        try:
            while self.is_running:
                msg = consumer.poll(1.0)
                if msg is None:
                    continue
                    
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        logger.debug(
                            f"End of partition reached for topic {msg.topic()} "
                            f"partition {msg.partition()} offset {msg.offset()}"
                        )
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
                    # Process the message
                    message_data = json.loads(msg.value().decode('utf-8'))
                    logger.info(f"Received message on topic {msg.topic()}: {message_data}")
                    
                    # Extract message UUID from key or value
                    message_uuid = msg.key().decode('utf-8') if msg.key() else None
                    if not message_uuid and isinstance(message_data, dict):
                        message_uuid = message_data.get('key')
                    
                    if message_uuid:
                        # Store the response in Redis
                        response_value = message_data.get('value') if isinstance(message_data, dict) else message_data
                        
                        # Extract user_email for user-specific storage
                        user_email = None
                        if isinstance(response_value, dict):
                            user_email = response_value.get('user_email')
                        
                        self.store_response_in_redis(message_uuid, response_value, user_email)
                        
                        logger.info(f"Processed message UUID: {message_uuid} from topic: {msg.topic()}" +
                                  (f" for user: {user_email}" if user_email else ""))
                    else:
                        logger.warning(f"No message UUID found in message: {message_data}")
                    
                    # Commit the message
                    consumer.commit(msg)
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse message as JSON: {str(e)}")
                    continue
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in consumer loop: {str(e)}")
        finally:
            consumer.close()
            logger.info(f"Consumer closed for topics: {topics}")

    def start_service(self):
        """Start the background consumer service"""
        if self.is_running:
            logger.warning("Service is already running")
            return
            
        self.is_running = True
        logger.info("Starting Kafka Consumer Service")
        
        # Start consumers for different topic groups
        all_topics = list(self.topic_configs.keys())
        
        # Create a single consumer thread for all response topics
        consumer_thread = threading.Thread(
            target=self.consume_topic_messages,
            args=(all_topics,),
            daemon=True
        )
        consumer_thread.start()
        self.threads.append(consumer_thread)
        
        logger.info("Kafka Consumer Service started successfully")

    def stop_service(self):
        """Stop the background consumer service"""
        logger.info("Stopping Kafka Consumer Service")
        self.is_running = False
        
        # Wait for threads to finish
        for thread in self.threads:
            thread.join(timeout=5)
        
        self.threads.clear()
        logger.info("Kafka Consumer Service stopped")

    def get_response_from_redis(self, message_uuid, timeout=30):
        """Get response from Redis by message UUID"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response_data = self.redis_client.get(f"kafka_response:{message_uuid}")
                if response_data:
                    # Delete the response after retrieving it
                    self.redis_client.delete(f"kafka_response:{message_uuid}")
                    return json.loads(response_data.decode('utf-8'))
            except Exception as e:
                logger.error(f"Error retrieving response from Redis: {str(e)}")
            
            time.sleep(0.5)  # Poll every 500ms
        
        logger.warning(f"Timeout waiting for response for UUID: {message_uuid}")
        return None

    def get_user_response_from_redis(self, message_uuid, user_email, timeout=30):
        """Get response from Redis by message UUID for a specific user"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Try user-specific key first
                response_data = self.redis_client.get(f"kafka_response_user:{user_email}:{message_uuid}")
                if response_data:
                    # Delete both user-specific and general keys
                    self.redis_client.delete(f"kafka_response_user:{user_email}:{message_uuid}")
                    self.redis_client.delete(f"kafka_response:{message_uuid}")
                    return json.loads(response_data.decode('utf-8'))
                
                # Fallback to general key
                response_data = self.redis_client.get(f"kafka_response:{message_uuid}")
                if response_data:
                    parsed_data = json.loads(response_data.decode('utf-8'))
                    # Check if this response is for the correct user
                    if isinstance(parsed_data, dict) and parsed_data.get('user_email') == user_email:
                        # Delete the response after retrieving it
                        self.redis_client.delete(f"kafka_response:{message_uuid}")
                        return parsed_data
                        
            except Exception as e:
                logger.error(f"Error retrieving user response from Redis: {str(e)}")
            
            time.sleep(0.5)  # Poll every 500ms
        
        logger.warning(f"Timeout waiting for response for UUID: {message_uuid} and user: {user_email}")
        return None


# Global service instance
kafka_service = KafkaConsumerService()


def start_kafka_consumer_service():
    """Start the global Kafka consumer service"""
    kafka_service.start_service()


def stop_kafka_consumer_service():
    """Stop the global Kafka consumer service"""
    kafka_service.stop_service()


def get_message_response(message_uuid, timeout=30):
    """Get message response from Redis"""
    return kafka_service.get_response_from_redis(message_uuid, timeout)


def get_user_message_response(message_uuid, user_email, timeout=30):
    """Get message response from Redis for a specific user"""
    return kafka_service.get_user_response_from_redis(message_uuid, user_email, timeout) 