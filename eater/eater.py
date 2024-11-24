import json
import uuid
import logging

from kafka_consumer import consume_messages
from kafka_producer import produce_message
from process_gpt import proces_food
from postgres import get_today_dishes

logger = logging.getLogger(__name__)

def process_messages():
    topics = ["photo-analysis-response", "get_today_data"]
    logging.info(f"Starting message processing with topics: {topics}")
    while True:
        for message, consumer in consume_messages(topics):
            try:
                value = message.value().decode("utf-8")
                value_dict = json.loads(value)
                consumer.commit(message)
                if message.topic() == "photo-analysis-response":
                    gpt_response = value_dict.get("value")
                    json_response = json.loads(gpt_response)
                    if json_response.get("error"):
                        logging.error(f"Error {json_response}")
                    else:
                        proces_food(json_response)
                elif message.topic() == "get_today_data":
                    today_dishes=get_today_dishes()
                    logger.info(f"Received request to get food")
                    message = {"key": str(uuid.uuid4()), "value": today_dishes}
                    produce_message(topic="send_today_data", message=message)
            except Exception as e:
                logging.error(f"Failed to process message: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting Eater processor")
    process_messages()