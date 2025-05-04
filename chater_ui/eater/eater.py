import logging

from .food_operations import delete_food
from .getter_eater import eater_get_today, get_recommendation
from .process_photo import eater_get_photo

logger = logging.getLogger(__name__)


def eater_photo(user_email):
    logger.info(f"Starting eater from chater for user: {user_email}")
    try:
        photo_confirmation = eater_get_photo(user_email=user_email)
        logger.info(f"Received photo confirmation {photo_confirmation}")
        return photo_confirmation
    except Exception as e:
        logger.info(f"Exception {e}")
        return "Failed"


def eater_today(user_email):
    logger.info(f"Returning food for today for user: {user_email}")
    try:
        today_food = eater_get_today(user_email=user_email)
    except Exception as e:
        logger.info(f"Exception {e}")
        return "Failed"
    return today_food


def delete_food_record(request, user_email):
    logger.info(f"Deleting food for user: {user_email}")
    try:
        return delete_food(request=request, user_email=user_email)
    except Exception as e:
        logger.info(f"Exception {e}")
        return "Failed"


def get_recommendations(request, user_email):
    logger.info(f"Requested recommendation providing for user: {user_email}")
    try:
        return get_recommendation(request=request, user_email=user_email)
    except Exception as e:
        logger.info(f"Exception {e}")
        return "Failed"
