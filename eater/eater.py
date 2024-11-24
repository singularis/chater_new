import json
import logging

from kafka_consumer import consume_messages
from kafka_producer import produce_message
from process_gpt import proces_food

logger = logging.getLogger(__name__)


def process_messages():
    topics = ["photo-analysis-response"]
    logging.info(f"Starting message processing with topics: {topics}")
    while True:
        for message, consumer in consume_messages(topics):
            try:
                value = message.value().decode("utf-8")
                value_dict = json.loads(value)
                consumer.commit(message)
                gpt_response = value_dict.get("value")
                json_response = json.loads(gpt_response)
                if json_response.get("error"):
                    logging.error(f"Error {json_response}")
                else:
                    proces_food(json_response)
            except Exception as e:
                logging.error(f"Failed to process message: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting Eater processor")
    process_messages()
