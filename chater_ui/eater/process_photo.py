from flask import request, jsonify
from kafka_producer import produce_message, create_producer
from kafka_consumer import consume_messages, create_consumer
from .proto import eater_photo_pb2
from common import get_prompt, resize_image, encode_image
import uuid
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def eater_get_photo():
    try:
        photo_message = eater_photo_pb2.PhotoMessage()
        photo_message.ParseFromString(request.data)

        time = photo_message.time
        photo_data = photo_message.photo_data
        logger.info(f"Received time: {time}")
        logger.info(f"Received photo_data size: {len(photo_data)} bytes")
        resized_photo_data = resize_image(photo_data, max_size=(1024, 1024))
        logger.info(f"Resized photo_data size: {len(resized_photo_data)} bytes")
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Optional: Save photo data to a file
        filename = f"/app/eater_storage/{current_time}.jpg"
        with open(filename, "wb") as image_file:
            image_file.write(resized_photo_data)
        logger.info(f"Photo saved to {current_time}.jpg")
        send_kafka_message(encode_image(filename))
        consumer = create_consumer(["photo-analysis-response-check"])
        for message in consume_messages(consumer):
            try:
                value = message.value().decode("utf-8")
                value_dict = json.loads(value)
                consumer.commit(message)
                return value_dict.get("value")
            except Exception as e:
                logger.error(f"Failed to process message: {e}")
                return "Timeout"
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({"message": "Failed to process the request", "error": str(e)}), 400

def send_kafka_message(photo_base64):
    producer = create_producer()
    photo_uuid = str(uuid.uuid4())
    prompt = get_prompt("default_prompt")
    message = {
        "key": photo_uuid,
        "value": {
            "prompt": prompt,
            "photo": photo_base64,
        },
    }
    logger.info(f"Food image {photo_uuid} send")
    produce_message(producer, topic="eater-send-photo", message=message)