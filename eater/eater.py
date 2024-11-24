from process_gpt import get_messages, proces_food
import logging
import json

logger = logging.getLogger(__name__)


gpt_response=get_messages(["photo-analysis-response"])
json_response = json.loads(gpt_response)
if json_response.get("error"):
    logging.error(f"Error {json_response}")
else:
    proces_food(json_response)