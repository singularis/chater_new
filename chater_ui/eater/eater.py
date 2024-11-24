from .process_photo import eater_get_photo
from .getter_eater import eater_get_today
import logging

logger = logging.getLogger(__name__)

def eater_photo():
    logger.info("Starting eater from chater")
    try:
        eater_get_photo()
    except Exception as e:
        logger.info(f"Exception {e}")
        return "Failed"
    return "Success"

def eater_today():
    logger.info("Returning food for today")
    try:
        today_food = eater_get_today()
    except Exception as e:
        logger.info(f"Exception {e}")
        return "Failed"
    return today_food
