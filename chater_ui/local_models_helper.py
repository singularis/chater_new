
import logging
import os
import requests
from user import get_user_model_tier

logger = logging.getLogger(__name__)

class LocalModelService:
    def __init__(self):
        self.local_model_service_url = os.getenv("LOCAL_MODEL_SERVICE_URL")
        self.default_model_tier = os.getenv("DEFAULT_MODEL_TIER", "cloud")
        self.local_model_kafka_topic = os.getenv("LOCAL_MODEL_KAFKA_TOPIC", "eater-send-photo-local")

    def _check_local_model_service_availability(self):
        if self.local_model_service_url:
            try:
                response = requests.get(self.local_model_service_url, timeout=0.1)
                if response.status_code == 200:
                    return True
                else:
                    logging.debug(f"Local model service returned status code: {response.status_code}")
                    return False
            except Exception as e:
                logging.error(f"Error checking local model service availability: {e}")
        return False

    def get_user_model_tier(self, user_email):
        if self._check_local_model_service_availability():
            return get_user_model_tier(user_email)
        else:
            return self.default_model_tier

    def get_user_kafka_topic(self, user_email, default_topic):
        try:
            user_model_tier = self.get_user_model_tier(user_email)
            if user_model_tier == "local":
                return self.local_model_kafka_topic
            else:
                return default_topic
        except Exception as e:
            logging.error(f"Error getting user kafka topic: {e}")
            return default_topic
