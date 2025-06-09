import json
import logging
import uuid

from common import remove_markdown_fence
from kafka_consumer import consume_messages, validate_user_data
from kafka_producer import produce_message
from postgres import delete_food, get_today_dishes, get_custom_date_dishes, modify_food
from process_gpt import get_recommendation, proces_food, process_weight

logger = logging.getLogger(__name__)


def process_messages():
    topics = [
        "photo-analysis-response",
        "get_today_data",
        "get_today_data_custom",
        "delete_food",
        "modify_food_record",
        "get_recommendation",
    ]
    logging.info(f"Starting message processing with topics: {topics}")
    while True:
        for message, consumer in consume_messages(topics):
            try:
                value = message.value().decode("utf-8")
                value_dict = json.loads(value)

                # Extract user_email from the message
                user_email = value_dict.get("value", {}).get("user_email")
                if not user_email:
                    logger.warning("No user_email found in message, skipping")
                    continue

                # Validate user data
                if not validate_user_data(value_dict, user_email):
                    logger.warning(
                        f"Invalid user data in message for user {user_email}, skipping"
                    )
                    continue

                # Get message key for tracking
                message_key = value_dict.get("key")
                if not message_key:
                    logger.warning(
                        f"No message key found for user {user_email}, skipping"
                    )
                    continue

                consumer.commit(message)

                if message.topic() == "photo-analysis-response":
                    gpt_response = value_dict.get("value", {})
                    if isinstance(gpt_response, str):
                        gpt_response = remove_markdown_fence(gpt_response)
                        json_response = json.loads(gpt_response)
                    else:
                        json_response = gpt_response

                    # Parse nested analysis if present
                    if "analysis" in json_response:
                        json_response = json.loads(json_response.get("analysis"))

                    # Check for errors after parsing
                    if json_response.get("error"):
                        logging.error(f"Error for user {user_email}: {json_response}")
                        produce_message(
                            topic="photo-analysis-response-check",
                            message={
                                "key": message_key,
                                "value": {
                                    "error": json_response.get("error"),
                                    "user_email": user_email,
                                },
                            },
                        )
                    else:
                        type_of_processing = json_response.get("type")
                        logger.info(
                            f"Received food processing {type_of_processing} for user {user_email}"
                        )
                        if type_of_processing == "food_processing":
                            logger.info(
                                f"Received food_process for user {user_email}: {json_response}"
                            )
                            proces_food(json_response, user_email)
                        elif type_of_processing == "weight_processing":
                            process_weight(json_response, user_email)
                        else:
                            produce_message(
                                topic="photo-analysis-response-check",
                                message={
                                    "key": message_key,
                                    "value": {
                                        "error": "unknown request",
                                        "user_email": user_email,
                                    },
                                },
                            )
                        produce_message(
                            topic="photo-analysis-response-check",
                            message={
                                "key": message_key,
                                "value": {
                                    "status": "Success",
                                    "user_email": user_email,
                                },
                            },
                        )
                elif message.topic() == "get_today_data":
                    today_dishes = get_today_dishes(user_email)
                    logger.info(f"Received request to get food for user {user_email}")
                    message = {
                        "key": message_key,
                        "value": {"dishes": today_dishes, "user_email": user_email},
                    }
                    produce_message(topic="send_today_data", message=message)
                elif message.topic() == "get_today_data_custom":
                    custom_date = value_dict.get("value", {}).get("date")
                    if not custom_date:
                        logger.warning(f"No date provided in custom date request for user {user_email}")
                        continue
                    custom_dishes = get_custom_date_dishes(custom_date, user_email)
                    logger.info(f"Received request to get food for {custom_date} for user {user_email}")
                    message = {
                        "key": message_key,
                        "value": {"dishes": custom_dishes, "user_email": user_email},
                    }
                    produce_message(topic="send_today_data_custom", message=message)
                elif message.topic() == "delete_food":
                    delete_food(value_dict.get("value"), user_email)
                    # Send confirmation
                    produce_message(
                        topic="delete_food_response",
                        message={
                            "key": message_key,
                            "value": {"status": "Success", "user_email": user_email},
                        },
                    )
                elif message.topic() == "modify_food_record":
                    modify_food(value_dict.get("value"), user_email)
                    # Send confirmation
                    produce_message(
                        topic="modify_food_record_response",
                        message={
                            "key": message_key,
                            "value": {"status": "Success", "user_email": user_email},
                        },
                    )
                elif message.topic() == "get_recommendation":
                    get_recommendation(message_key,value_dict.get("value"), user_email)
            except Exception as e:
                logging.error(
                    f"Failed to process message for user {user_email}: {e}, message {value_dict}"
                )
                # Send error response if we have a message key
                if message_key:
                    produce_message(
                        topic="error_response",
                        message={
                            "key": message_key,
                            "value": {"error": str(e), "user_email": user_email},
                        },
                    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting Eater processor")
    process_messages()
