import base64
import logging
import os
import uuid
from datetime import datetime

from flask import jsonify, request, current_app

from common import get_prompt, get_respond_in_language, resize_image
from kafka_consumer_service import get_user_message_response
from kafka_producer import create_producer, produce_message

from .proto import eater_photo_pb2
from minio_utils import put_bytes

logger = logging.getLogger(__name__)


def eater_get_photo(user_email):
    try:
        photo_message = eater_photo_pb2.PhotoMessage()
        photo_message.ParseFromString(request.data)

        time = photo_message.time
        photo_data = photo_message.photo_data
        type_of_processing = photo_message.photoType
        logger.info(f"Received time for user {user_email}: {time}")
        logger.info(
            f"Received photo_data size for user {user_email}: {len(photo_data)} bytes"
        )
        logger.info(f"Received task type for user {user_email}: {type_of_processing}")
        resized_photo_data = resize_image(photo_data, max_size=(1024, 1024))
        logger.info(
            f"Resized photo_data size for user {user_email}: {len(resized_photo_data)} bytes"
        )
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        object_name = f"{user_email}/{current_time}.jpg"

        # Upload to MinIO (eater bucket)
        client = current_app.config.get("MINIO_CLIENT")
        if client is None:
            raise RuntimeError("MINIO client is not initialized")
        bucket_name = os.getenv("MINIO_BUCKET_EATER", "eater")
        put_bytes(client, bucket_name, object_name, resized_photo_data, content_type="image/jpeg")
        logger.info(f"Photo uploaded to MinIO at {bucket_name}/{object_name} for user {user_email}")

        # Generate a unique message ID for tracking
        message_id = str(uuid.uuid4())
        # Encode photo directly from memory to avoid filesystem dependency
        photo_base64 = base64.b64encode(resized_photo_data).decode("utf-8")
        send_kafka_message(photo_base64, type_of_processing, user_email, message_id=message_id)

        logger.info(
            f"Waiting for photo analysis response for user {user_email} with message ID {message_id}"
        )

        # Get response from Redis using the background consumer service
        try:
            response = get_user_message_response(message_id, user_email, timeout=30)
            if response is not None:
                logger.info(
                    f"Retrieved photo analysis response for user {user_email}: {response}"
                )

                if response.get("error"):
                    logger.error(
                        f"Error in photo analysis response for user {user_email}: {response.get('error')}"
                    )
                    return jsonify({"error": response.get("error")}), 400

                return response.get("status", "Success")
            else:
                logger.warning(
                    f"Timeout waiting for photo analysis response for user {user_email} with message ID {message_id}"
                )
                return "Timeout", 408
        except Exception as e:
            logger.error(
                f"Failed to get photo analysis response for user {user_email}: {e}"
            )
            return "Timeout", 408

    except Exception as e:
        logger.error(f"Error processing request for user {user_email}: {str(e)}")
        return (
            jsonify({"message": "Failed to process the request", "error": str(e)}),
            400,
        )


def send_kafka_message(
    photo_base64,
    type_of_processing,
    user_email,
    message_id=None,
    topic="eater-send-photo",
):
    producer = create_producer()
    photo_uuid = message_id or str(uuid.uuid4())
    prompt = get_prompt(type_of_processing)
    try:
        lang_instruction = get_prompt("respond_in_language")
        user_lang = get_respond_in_language(user_email)
        prompt = f"{prompt}\n{lang_instruction}\nTarget language: {user_lang}"
    except Exception:
        pass
    message = {
        "key": photo_uuid,
        "value": {
            "prompt": prompt,
            "photo": photo_base64,
            "user_email": user_email,
        },
    }
    logger.info(f"Food image {photo_uuid} sent for user {user_email}")
    if type_of_processing == "weight_prompt":
        topic = "chater-vision"
        logger.info(f"Topic: {topic} for user {user_email}")
    produce_message(producer, topic=topic, message=message)
