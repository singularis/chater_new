import json
import logging
import uuid

from flask import jsonify
from kafka_consumer_service import get_user_message_response
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

        logger.info(f"Waiting for delete confirmation for user {user_email} with message ID {message_id}")
        
        # Get response from Redis using the background consumer service
        try:
            response = get_user_message_response(message_id, user_email, timeout=30)
            if response is not None:
                logger.info(f"Retrieved delete confirmation for user {user_email}: {response}")
                
                if response.get("error"):
                    logger.error(f"Error in delete response for user {user_email}: {response.get('error')}")
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
            else:
                logger.warning(f"Timeout waiting for delete confirmation for user {user_email} with message ID {message_id}")
                delete_food_response.success = False
                response_data = delete_food_response.SerializeToString()
                return (
                    response_data,
                    500,
                    {"Content-Type": "application/grpc+proto"},
                )
        except Exception as e:
            logger.error(f"Failed to get delete confirmation for user {user_email}: {e}")
            delete_food_response.success = False
            response_data = delete_food_response.SerializeToString()
            return (
                response_data,
                500,
                {"Content-Type": "application/grpc+proto"},
            )

    except Exception as e:
        logger.error(f"Error in delete_food for user {user_email}: {str(e)}")
        delete_food_response.success = False
        response_data = delete_food_response.SerializeToString()
        return response_data, 500, {"Content-Type": "application/grpc+proto"}
