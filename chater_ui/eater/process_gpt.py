from kafka_consumer import consume_messages, create_consumer
import json
import logging


logger = logging.getLogger(__name__)


def get_messages(topics):
    logger.info(
        f"Starting message processing with topics: {topics}"
    )
    consumer = create_consumer(topics)
    for message in consume_messages(consumer):
        try:
            value = message.value().decode("utf-8")
            value_dict = json.loads(value)
            consumer.commit(message)
            return value_dict.get("value")
        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            return "Timeout"

def proces_food(message):
    logger.info("Starting processing received food")
    try:
        dish_name = message.get("dish_name")
        estimated_avg_calories = message.get("estimated_avg_calories")
        ingredients = message.get("ingredients")
        total_awg_weight = message.get("total_avg_weight")
        contains = message.get("contains")
        logger.info(f"Found dish {dish_name}, with {estimated_avg_calories} calories, contains ingredients {ingredients}, weight {total_awg_weight}, and nutrients {contains}")

    except Exception as e:
        logger.info(f"Somthing went wrong during processing, {e}")
        raise

