from .process_photo import eater_get_photo
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