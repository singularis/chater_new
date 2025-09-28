import base64
import logging
import os
import threading
import uuid
from datetime import datetime

from flask import current_app, jsonify, request

from common import get_prompt, get_respond_in_language, resize_image
from kafka_consumer_service import get_user_message_response
from kafka_producer import KafkaDispatchError, send_kafka_message
from minio_utils import put_bytes

from .proto import eater_photo_pb2

logger = logging.getLogger(__name__)


def _upload_to_minio_background(
    minio_client, bucket_name, object_name, photo_bytes, user_email
):
    try:
        put_bytes(
            minio_client,
            bucket_name,
            object_name,
            photo_bytes,
            content_type="image/jpeg",
        )
        logger.info(
            "Photo uploaded to MinIO at %s/%s for user %s",
            bucket_name,
            object_name,
            user_email,
        )
    except Exception as exc:
        logger.exception(
            "Error uploading photo to MinIO for user %s: %s", user_email, exc
        )


def eater_get_photo(user_email, local_model_service):
    try:
        photo_message = eater_photo_pb2.PhotoMessage()
        photo_message.ParseFromString(request.data)

        time = photo_message.time
        photo_data = photo_message.photo_data
        type_of_processing = photo_message.photoType
        logger.debug("Received photo metadata for user %s", user_email)
        logger.debug(
            "Raw photo payload size for user %s: %s bytes", user_email, len(photo_data)
        )
        logger.debug("Task type for user %s: %s", user_email, type_of_processing)
        resized_photo_data = resize_image(photo_data, max_size=(1024, 1024))
        logger.debug(
            "Resized photo payload size for user %s: %s bytes",
            user_email,
            len(resized_photo_data),
        )
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        object_name = f"{user_email}/{current_time}.jpg"

        # Generate a unique message ID for tracking
        message_id = str(uuid.uuid4())
        # Encode photo directly from memory to avoid filesystem dependency
        photo_base64 = base64.b64encode(resized_photo_data).decode("utf-8")
        try:
            _dispatch_photo_message(
                photo_base64,
                type_of_processing,
                user_email,
                message_id,
                local_model_service,
            )
        except KafkaDispatchError as kafka_error:
            logger.error(
                "Failed to dispatch photo request for user %s: %s",
                user_email,
                kafka_error,
            )
            return (
                jsonify({"message": "Kafka dispatch failed", "error": str(kafka_error)}),
                kafka_error.status_code,
            )

        logger.info(
            "Waiting for photo analysis response for user %s (message_id=%s)",
            user_email,
            message_id,
        )

        # Get response from Redis using the background consumer service
        try:
            response = get_user_message_response(message_id, user_email, timeout=60)
            if response is not None:
                logger.debug(
                    "Retrieved photo analysis response for user %s", user_email
                )

                if response.get("error"):
                    logger.error(
                        "Error in photo analysis response for user %s: %s",
                        user_email,
                        response.get("error"),
                    )
                    return jsonify({"error": response.get("error")}), 400
                else:
                    # Trigger MinIO upload in background; do not block the response
                    client = current_app.config.get("MINIO_CLIENT")
                    bucket_name = os.getenv("MINIO_BUCKET_EATER", "eater")
                    if client is None:
                        logger.error("MINIO client is not initialized; skipping upload")
                    else:
                        threading.Thread(
                            target=_upload_to_minio_background,
                            args=(
                                client,
                                bucket_name,
                                object_name,
                                resized_photo_data,
                                user_email,
                            ),
                            daemon=True,
                        ).start()
                    return response.get("status", "Success")
            else:
                logger.warning(
                    "Timeout waiting for photo analysis response for user %s (message_id=%s)",
                    user_email,
                    message_id,
                )
                return "Timeout", 408
        except Exception as exc:
            logger.exception(
                "Failed to get photo analysis response for user %s", user_email
            )
            return "Timeout", 408

    except Exception as exc:
        logger.exception("Error processing request for user %s", user_email)
        return (
            jsonify({"message": "Failed to process the request", "error": str(exc)}),
            400,
        )


def _dispatch_photo_message(
    photo_base64,
    type_of_processing,
    user_email,
    message_id,
    local_model_service,
    topic="eater-send-photo",
):
    photo_uuid = message_id or str(uuid.uuid4())
    prompt = get_prompt(type_of_processing)
    try:
        lang_instruction = get_prompt("respond_in_language")
        user_lang = get_respond_in_language(user_email)
        prompt = f"{prompt}\n{lang_instruction}\nTarget language: {user_lang}"
    except Exception:
        pass
    payload = {
        "prompt": prompt,
        "photo": photo_base64,
        "user_email": user_email,
    }
    logger.debug("Food image %s queued for user %s", photo_uuid, user_email)
    destination_topic = topic
    if type_of_processing == "weight_prompt":
        destination_topic = "chater-vision"
        logger.debug(
            "Routing weight prompt for user %s to topic %s", user_email, destination_topic
        )
    elif type_of_processing == "eater-send-photo":
        if local_model_service:
            destination_topic = local_model_service.get_user_kafka_topic(
                user_email, topic
            )
        else:
            logger.warning(
                "User model tier lookup unavailable; using default topic %s for user %s",
                destination_topic,
                user_email,
            )
    elif type_of_processing not in {"eater-send-photo", "weight_prompt"}:
        logger.error(
            "Invalid processing type %s for user %s; using default topic %s",
            type_of_processing,
            user_email,
            destination_topic,
        )

    send_kafka_message(
        destination_topic,
        value=payload,
        key=photo_uuid,
        ensure_user_email=True,
    )
