import json
import logging
import uuid

from kafka_consumer import consume_messages
from kafka_producer import produce_message
from postgres import delete_food, get_today_dishes
from process_gpt import proces_food, process_weight

logger = logging.getLogger(__name__)


def process_messages():
    topics = ["photo-analysis-response", "get_today_data", "delete_food"]
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
                    id = str(uuid.uuid4())
                    if json_response.get("error"):
                        logging.error(f"Error {json_response}")
                        produce_message(
                            topic="photo-analysis-response-check",
                            message={"key": id, "value": json_response.get("error")},
                        )
                    else:
                        type_of_processing = json_response.get("type")
                        if type_of_processing == "food_processing":
                            proces_food(json_response)
                        elif type_of_processing == "weight_processing":
                            process_weight(json_response)
                        else:
                            produce_message(
                                topic="photo-analysis-response-check",
                                message={"key": id, "value": "unknown request"},
                            )
                        produce_message(
                            topic="photo-analysis-response-check",
                            message={"key": id, "value": "Success"},
                        )
                elif message.topic() == "get_today_data":
                    today_dishes = get_today_dishes()
                    logger.info(f"Received request to get food")
                    message = {"key": str(uuid.uuid4()), "value": today_dishes}
                    produce_message(topic="send_today_data", message=message)
                elif message.topic() == "delete_food":
                    delete_food(value_dict.get("value"))
            except Exception as e:
                logging.error(f"Failed to process message: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting Eater processor")
    process_messages()
