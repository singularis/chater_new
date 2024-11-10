from .process_photo import eater_get_photo
from .process_gpt import get_messages, proces_food
import logging
import json

logger = logging.getLogger(__name__)

logger.info("Starting eater")

def eater_photo():
    try:
        eater_get_photo()
        gpt_response=get_messages(["photo-analysis-response"])
        json_response = json.loads(gpt_response)
        if json_response.get("error"):
            logging.error(f"Error {json_response}")
            return f"ERROR: {json_response}"
        else:
            proces_food(json_response)
    except Exception as e:
        logger.info(f"Exception {e}")
        return "Failed"
    return "Success"