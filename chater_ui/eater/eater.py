import logging

from .food_operations import delete_food
from .getter_eater import eater_get_today, get_recommendation
from .process_photo import eater_get_photo

logger = logging.getLogger(__name__)


def eater_photo():
    logger.info("Starting eater from chater")
    try:
        photo_confirmation = eater_get_photo()
        logger.info(f"Received photo confirmation {photo_confirmation}")
        return photo_confirmation
    except Exception as e:
        logger.info(f"Exception {e}")
        return "Failed"


def eater_today():
    logger.info("Returning food for today")
    try:
        today_food = eater_get_today()
    except Exception as e:
        logger.info(f"Exception {e}")
        return "Failed"
    return today_food


def delete_food_record(request):
    logger.info("Deleting food")
    try:
        return delete_food(request=request)
    except Exception as e:
        logger.info(f"Exception {e}")
        return "Failed"

def get_recommendations(request):
    logger.info("Requested recommendation providing")
    try:
        return get_recommendation(request=request)
    except Exception as e:
        logger.info(f"Exception {e}")
        return "Failed"
