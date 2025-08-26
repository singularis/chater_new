import logging

from .food_operations import delete_food, modify_food_record, manual_weight
from .language import set_language_handler
from .food_operations import get_alcohol_latest, get_alcohol_range
from .getter_eater import eater_get_today, eater_get_custom_date, get_recommendation, eater_auth_token
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


def eater_custom_date(request, user_email):
    logger.info(f"Returning food for custom date for user: {user_email}")
    try:
        custom_date_food = eater_get_custom_date(request=request, user_email=user_email)
    except Exception as e:
        logger.info(f"Exception {e}")
        return "Failed"
    return custom_date_food


def delete_food_record(request, user_email):
    logger.info(f"Deleting food for user: {user_email}")
    try:
        return delete_food(request=request, user_email=user_email)
    except Exception as e:
        logger.info(f"Exception {e}")
        return "Failed"


def modify_food_record_data(request, user_email):
    logger.info(f"Modifying food record for user: {user_email}")
    try:
        return modify_food_record(request=request, user_email=user_email)
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


def eater_auth_request(request):
    logger.info("Processing eater authentication request")
    try:
        auth_response = eater_auth_token(request=request)
    except Exception as e:
        logger.info(f"Exception in auth request: {e}")
        return "Failed"
    return auth_response


def manual_weight_record(request, user_email):
    logger.info(f"Processing manual weight for user: {user_email}")
    try:
        return manual_weight(request=request, user_email=user_email)
    except Exception as e:
        logger.info(f"Exception {e}")
        return "Failed"


def alcohol_latest(user_email):
    logger.info(f"Fetching alcohol latest summary for user: {user_email}")
    try:
        return get_alcohol_latest(user_email=user_email)
    except Exception as e:
        logger.info(f"Exception {e}")
        return "Failed"


def alcohol_range(request, user_email):
    logger.info(f"Fetching alcohol range for user: {user_email}")
    try:
        return get_alcohol_range(request=request, user_email=user_email)
    except Exception as e:
        logger.info(f"Exception {e}")
        return "Failed"


def set_language(request, user_email):
    logger.info(f"Setting language for user: {user_email}")
    try:
        return set_language_handler(request=request, user_email=user_email)
    except Exception as e:
        logger.info(f"Exception {e}")
        return "Failed"