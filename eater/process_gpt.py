import json
import logging
import uuid

from kafka_producer import produce_message
from postgres import get_dishes, write_to_dish_day, write_weight

logger = logging.getLogger(__name__)


def proces_food(message):
    logger.info("Starting processing received food")
    try:
        dish_name = message.get("dish_name")
        estimated_avg_calories = message.get("estimated_avg_calories")
        ingredients = message.get("ingredients")
        total_awg_weight = message.get("total_avg_weight")
        contains = message.get("contains")
        logger.info(
            f"Found dish {dish_name}, with {estimated_avg_calories} calories, contains ingredients {ingredients}, weight {total_awg_weight}, and nutrients {contains}"
        )
        write_to_dish_day(message=message)

    except Exception as e:
        logger.info(f"Somthing went wrong during processing, {e}")
        raise


def process_weight(message):
    weight = message.get("weight")
    logger.info(f"Starting processing received weight {weight}")
    write_weight(weight=weight)


def get_recommendation(message):
    logger.info("Received request to get recommendation")
    days = message.get("days")
    prompt = message.get("prompt", "")
    food_table = get_dishes(days=days)
    id = str(uuid.uuid4())
    logger.info(f"Payload {days}, {prompt}, food table {food_table}")
    if food_table:
        try:
            payload = {
                "key": id,
                "value": {"question": str(f"{prompt} Food Table: {food_table}")},
            }
            produce_message(topic="gemini-send", message=payload)
            logger.info(f"formatted_payload {payload}")
        except Exception as e:
            logger.error(f"Error formatting payload: {e}")
            return
