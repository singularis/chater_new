import logging
import threading

from app.trnd_processor import (_generate_and_cache_recommendation_background,
                                cache_recommendation,
                                get_cached_recommendation)
from local_models_helper import LocalModelService

from .food_operations import (delete_food, get_alcohol_latest,
                              get_alcohol_range, manual_weight,
                              modify_food_record)
from .getter_eater import (eater_auth_token, eater_get_custom_date,
                           eater_get_today, get_recommendation)
from .language import set_language_handler
from .process_photo import eater_get_photo

logger = logging.getLogger(__name__)
local_model_service = LocalModelService()


def eater_photo(user_email):
    logger.info("Photo request received", extra={"user_email": user_email})
    try:
        photo_confirmation = eater_get_photo(
            user_email=user_email, local_model_service=local_model_service
        )
        logger.debug("Photo confirmation payload: %s", photo_confirmation)

        if photo_confirmation == "Success":
            logger.info(
                "Photo processed successfully, triggering background recommendation for user: %s",
                user_email,
            )
            threading.Thread(
                target=_generate_and_cache_recommendation_background,
                args=(user_email,),
                daemon=True,
            ).start()

        return photo_confirmation
    except Exception as exc:
        logger.exception("Photo processing failed for user %s", user_email)
        return "Failed"


def eater_today(user_email):
    logger.info("Fetching today meals", extra={"user_email": user_email})
    try:
        return eater_get_today(user_email=user_email)
    except Exception:
        logger.exception("Failed to fetch today's meals for user %s", user_email)
        return "Failed"


def eater_custom_date(request, user_email):
    logger.info("Fetching meals for custom date", extra={"user_email": user_email})
    try:
        return eater_get_custom_date(request=request, user_email=user_email)
    except Exception:
        logger.exception(
            "Failed to fetch meals for requested date for user %s", user_email
        )
        return "Failed"


def delete_food_record(request, user_email):
    logger.info("Deleting food entry", extra={"user_email": user_email})
    try:
        return delete_food(request=request, user_email=user_email)
    except Exception:
        logger.exception("Failed to delete food entry for user %s", user_email)
        return "Failed"


def modify_food_record_data(request, user_email):
    logger.info("Updating food record", extra={"user_email": user_email})
    try:
        return modify_food_record(request=request, user_email=user_email)
    except Exception:
        logger.exception("Failed to update food record for user %s", user_email)
        return "Failed"


def get_recommendations(request, user_email, skip_cache: bool = False):
    logger.info("Generating recommendations", extra={"user_email": user_email})
    try:
        # Check cache first (unless explicitly skipped)
        if not skip_cache:
            cached = get_cached_recommendation(user_email)
            if cached:
                logger.info("Returning cached recommendation for user: %s", user_email)
                return cached, 200, {"Content-Type": "application/protobuf"}

        # Cache miss or skip_cache - generate fresh recommendation
        logger.debug("Generating fresh recommendation for user: %s", user_email)
        result = get_recommendation(
            request=request,
            user_email=user_email,
            local_model_service=local_model_service,
        )

        # Cache the result if successful
        if result and isinstance(result, tuple) and len(result) >= 2:
            data, status_code = result[0], result[1]
            if status_code == 200 and data:
                cache_recommendation(user_email, data)

        return result
    except Exception:
        logger.exception("Failed to generate recommendations for user %s", user_email)
        return "Failed"


def eater_auth_request(request):
    logger.info("Processing eater authentication request")
    try:
        return eater_auth_token(request=request)
    except Exception:
        logger.exception("Eater authentication failed")
        return "Failed"


def manual_weight_record(request, user_email):
    logger.info("Recording manual weight", extra={"user_email": user_email})
    try:
        return manual_weight(request=request, user_email=user_email)
    except Exception:
        logger.exception("Failed to record manual weight for user %s", user_email)
        return "Failed"


def alcohol_latest(user_email):
    logger.info("Fetching latest alcohol summary", extra={"user_email": user_email})
    try:
        return get_alcohol_latest(user_email=user_email)
    except Exception:
        logger.exception(
            "Failed to retrieve latest alcohol summary for user %s", user_email
        )
        return "Failed"


def alcohol_range(request, user_email):
    logger.info("Fetching alcohol range", extra={"user_email": user_email})
    try:
        return get_alcohol_range(request=request, user_email=user_email)
    except Exception:
        logger.exception("Failed to retrieve alcohol range for user %s", user_email)
        return "Failed"


def set_language(request, user_email):
    logger.info("Setting language preference", extra={"user_email": user_email})
    try:
        return set_language_handler(request=request, user_email=user_email)
    except Exception:
        logger.exception("Failed to set language for user %s", user_email)
        return "Failed"
