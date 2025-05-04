import json
import logging
import uuid

from flask import jsonify
from kafka_consumer import consume_messages, create_consumer
from kafka_producer import create_producer, produce_message

from .proto import delete_food_pb2

logger = logging.getLogger(__name__)


def delete_food(request, user_email):
    delete_food_response = delete_food_pb2.DeleteFoodResponse()
    delete_food_request = delete_food_pb2.DeleteFoodRequest()
    try:
        proto_data = request.data
        if not proto_data:
            logger.error(
                f"No Protobuf data found in the request from user: {user_email}"
            )
            return jsonify({"success": False, "error": "Invalid Protobuf data"}), 400

        delete_food_request.ParseFromString(proto_data)
        time = delete_food_request.time
        logger.info(f"Extracted time from Protobuf for user {user_email}: {time}")

        producer = create_producer()
        message_id = str(uuid.uuid4())
        message = {"key": message_id, "value": {"time": time, "user_email": user_email}}
        produce_message(producer, topic="delete_food", message=message)
        logger.info(f"Sent message to Kafka for user {user_email}: {message}")

        # Wait for confirmation
        consumer = create_consumer(["delete_food_response"])
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            for response_message in consume_messages(
                consumer, expected_user_email=user_email
            ):
                try:
                    value = response_message.value().decode("utf-8")
                    value_dict = json.loads(value)

                    # Verify this is the response for our request
                    if value_dict.get("key") != message_id:
                        logger.info(
                            f"Skipping message with different key for user {user_email}"
                        )
                        continue

                    # Verify this is for our user
                    if value_dict.get("value", {}).get("user_email") != user_email:
                        logger.info(
                            f"Skipping message for different user: {value_dict.get('value', {}).get('user_email')}"
                        )
                        continue

                    consumer.commit(response_message)
                    response_value = value_dict.get("value")

                    if response_value.get("error"):
                        logger.error(
                            f"Error in response for user {user_email}: {response_value.get('error')}"
                        )
                        delete_food_response.success = False
                        response_data = delete_food_response.SerializeToString()
                        return (
                            response_data,
                            500,
                            {"Content-Type": "application/grpc+proto"},
                        )

                    delete_food_response.success = True
                    response_data = delete_food_response.SerializeToString()
                    return (
                        response_data,
                        200,
                        {"Content-Type": "application/grpc+proto"},
                    )

                except Exception as e:
                    logger.error(
                        f"Failed to process message for user {user_email}: {e}"
                    )
                    retry_count += 1
                    if retry_count >= max_retries:
                        delete_food_response.success = False
                        response_data = delete_food_response.SerializeToString()
                        return (
                            response_data,
                            500,
                            {"Content-Type": "application/grpc+proto"},
                        )
                    continue

        delete_food_response.success = False
        response_data = delete_food_response.SerializeToString()
        return response_data, 500, {"Content-Type": "application/grpc+proto"}

    except Exception as e:
        logger.error(f"Error in delete_food for user {user_email}: {str(e)}")
        delete_food_response.success = False
        response_data = delete_food_response.SerializeToString()
        return response_data, 500, {"Content-Type": "application/grpc+proto"}
