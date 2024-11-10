from flask import request, jsonify
import logging
from .proto import eater_photo_pb2
import uuid
import base64
from datetime import datetime
from kafka_producer import produce_message, create_producer
from common import get_prompt

logger = logging.getLogger(__name__)
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")


def eater_get_photo():
    try:
        photo_message = eater_photo_pb2.PhotoMessage()
        photo_message.ParseFromString(request.data)

        time = photo_message.time
        photo_data = photo_message.photo_data
        logger.info(f"Received time: {time}")
        logger.info(f"Received photo_data size: {len(photo_data)} bytes")
        send_kafka_message(photo_data)

        # Optional: Save photo data to a file
        filename = f"{current_time}.jpg"
        # TODO Save photo to persistent storage
        with open(filename, "wb") as image_file:
            image_file.write(photo_data)
        logger.info("Photo saved to received_image.jpg")

        return jsonify({"message": "Photo received successfully!", "time": time}), 200
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({"message": "Failed to process the request", "error": str(e)}), 400

def send_kafka_message(photo):
    producer = create_producer()
    photo_uuid = str(uuid.uuid4())
    prompt = get_prompt("default_prompt")
    message = {
        "key": photo_uuid,
        "value": {
            "prompt": prompt,
            "photo": base64.b64encode(photo).decode("utf-8"),
        },
    }
    logger.info(f"Food image {photo_uuid} send")
    produce_message(producer, topic="eater-send-photo", message=message)