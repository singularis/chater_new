import logging

from postgres import write_to_dish_day, write_weight

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
