from kafka_producer import produce_message, create_producer
from kafka_consumer import consume_messages, create_consumer
import logging
import json
import uuid
from datetime import datetime


logger = logging.getLogger(__name__)



def eater_get_today():
    producer = create_producer()
    logger.info(f"Received request to get food")
    message = {
        "key": str(uuid.uuid4()),
        "value": {
            "date":  datetime.now().strftime("%d-%m-%Y"),
        },
    }
    produce_message(producer, topic="get_today_data", message=message)
    logger.info(f"Listening Kafka to get today")
    consumer = create_consumer(["send_today_data"])
    for message in consume_messages(consumer):
        try:
            value = message.value().decode("utf-8")
            value_dict = json.loads(value)
            consumer.commit(message)
            return value_dict.get("value")
        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            return "Timeout"