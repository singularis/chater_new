import json
import logging
import uuid

from kafka_producer import produce_message
from postgres import get_dishes, write_to_dish_day, write_weight

logger = logging.getLogger(__name__)


def process_food(message, user_email):
    logger.debug(f"Starting food processing for user {user_email}")
    try:
        dish_name = message.get("dish_name")
        estimated_avg_calories = message.get("estimated_avg_calories")
        ingredients = message.get("ingredients")
        total_awg_weight = message.get("total_avg_weight")
        contains = message.get("contains")

        if not all(
            [dish_name, estimated_avg_calories, ingredients, total_awg_weight, contains]
        ):
            logger.error(
                f"Missing required fields in food processing for user {user_email}"
            )
            raise ValueError("Missing required fields in food processing")

        # Ensure image_id is preserved if present in message
        if "image_id" not in message:
            logger.debug(f"No image_id found in message for user {user_email}")

        logger.debug(
            f"Found dish {dish_name} for user {user_email}, with {estimated_avg_calories} calories, "
            f"contains ingredients {ingredients}, weight {total_awg_weight}, and nutrients {contains}"
        )
        write_to_dish_day(message=message, user_email=user_email)
        logger.debug(f"Successfully processed food for user {user_email}")

    except Exception as e:
        logger.error(f"Error during food processing for user {user_email}: {str(e)}")
        raise


def process_weight(message, user_email):
    logger.debug(f"Starting weight processing for user {user_email}")
    try:
        weight = message.get("weight")
        if not weight:
            logger.error(f"Missing weight in message for user {user_email}")
            raise ValueError("Missing weight in message")

        logger.debug(f"Processing weight {weight} for user {user_email}")
        write_weight(weight=weight, user_email=user_email)
        logger.debug(f"Successfully processed weight for user {user_email}")

    except Exception as e:
        logger.error(f"Error during weight processing for user {user_email}: {str(e)}")
        raise


def get_recommendation(message_key, message, value_dict, user_email):
    logger.debug(f"Received request to get recommendation for user {user_email}")
    days = message.get("days")
    prompt = message.get("prompt", "")
    model_topic = message.get("model_topic") or value_dict.get("value", {}).get(
        "model_topic", ""
    )
    food_table = get_dishes(days=days, user_email=user_email)
    id = message_key
    logger.debug(
        f"Payload for user {user_email}: {days}, {prompt}, food table {food_table}"
    )

    try:
        if food_table:
            # User has food data, send normal recommendation request
            payload = {
                "key": id,
                "value": {
                    "question": str(f"{prompt} Food Table: {food_table}"),
                    "user_email": user_email,
                },
            }
            logger.debug(f"model_topic for user {user_email}: {model_topic}")
            if model_topic == "eater-send-photo-local":
                topic = model_topic
            else:
                topic = "gemini-send"
            produce_message(topic=topic, message=payload)
            logger.debug(f"formatted_payload for user {user_email}: {payload}")
        else:
            # No food data found for user, send specific message
            no_food_message = "Respond with exactly this message: 'NO FOOD RECORDS FOUND FOR USER. Please record your food before using this feature.' Do not provide any additional text, analysis, or recommendations. Only respond with this exact message."
            payload = {
                "key": id,
                "value": {
                    "question": no_food_message,
                    "user_email": user_email,
                },
            }
            produce_message(topic="gemini-send", message=payload)
            logger.debug(
                f"No food data found. Sent no-food message for user {user_email}: {payload}"
            )
    except Exception as e:
        logger.error(f"Error formatting payload for user {user_email}: {e}")
        return
