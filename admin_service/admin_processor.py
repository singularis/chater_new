import logging
import json
from kafka_consumer import consume_messages, create_consumer
from postgres import save_admin_data, create_admin_table

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_admin_messages():
    """Main processor to consume admin messages and write to database."""
    logger.info("Starting admin processor")
    
    # Initialize database
    try:
        create_admin_table()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    # Topics to consume from
    topics = ["feedback"]
    
    # Create consumer
    consumer = create_consumer(topics)
    
    try:
        # Start consuming messages
        while True:
            try:
                for message in consume_messages(consumer):
                    try:
                        value = message.value().decode("utf-8")
                        value_dict = json.loads(value)
                        
                        # Extract admin data
                        admin_info = value_dict.get("value", {})
                        admin_time = admin_info.get("time")
                        user_email = admin_info.get("user_email")
                        admin_text = admin_info.get("feedback")
                        
                        if not all([admin_time, user_email, admin_text]):
                            logger.warning(f"Incomplete admin data: {value_dict}")
                            continue
                        
                        logger.info(f"Processing admin data from {user_email}")
                        
                        # Save admin data to database
                        admin_id = save_admin_data(user_email, admin_text, admin_time)
                        
                        # Commit the Kafka message
                        consumer.commit(message)
                        
                        logger.info(f"Successfully processed admin data {admin_id} from {user_email}")
                        
                    except Exception as e:
                        logger.error(f"Error processing admin message: {e}")
                        # Don't commit the message if there's an error
                        continue
                        
            except Exception as e:
                logger.error(f"Error in admin processor: {e}")
                # Add a small delay before retrying
                import time
                time.sleep(5)
    finally:
        # Clean up consumer
        try:
            consumer.close()
            logger.info("Consumer closed successfully")
        except Exception as e:
            logger.error(f"Error closing consumer: {e}")


if __name__ == "__main__":
    logger.info("Starting Admin Processor")
    process_admin_messages() 