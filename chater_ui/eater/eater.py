from .process_photo import eater_get_photo
from .getter_eater import eater_get_today
from .food_operations import delete_food
import logging

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