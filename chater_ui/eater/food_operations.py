import json
import logging
import uuid

from flask import jsonify

from kafka_consumer_service import get_user_message_response
from kafka_producer import create_producer, produce_message

from .proto import (
    alcohol_pb2,
    delete_food_pb2,
    manual_weight_pb2,
    modify_food_record_pb2,
)

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

        logger.info(
            f"Waiting for delete confirmation for user {user_email} with message ID {message_id}"
        )

        # Get response from Redis using the background consumer service
        try:
            response = get_user_message_response(message_id, user_email, timeout=30)
            if response is not None:
                logger.info(
                    f"Retrieved delete confirmation for user {user_email}: {response}"
                )

                if response.get("error"):
                    logger.error(
                        f"Error in delete response for user {user_email}: {response.get('error')}"
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
            else:
                logger.warning(
                    f"Timeout waiting for delete confirmation for user {user_email} with message ID {message_id}"
                )
                delete_food_response.success = False
                response_data = delete_food_response.SerializeToString()
                return (
                    response_data,
                    500,
                    {"Content-Type": "application/grpc+proto"},
                )
        except Exception as e:
            logger.error(
                f"Failed to get delete confirmation for user {user_email}: {e}"
            )
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


def modify_food_record(request, user_email):
    modify_food_response = modify_food_record_pb2.ModifyFoodRecordResponse()
    modify_food_request = modify_food_record_pb2.ModifyFoodRecordRequest()
    try:
        proto_data = request.data
        if not proto_data:
            logger.error(
                f"No Protobuf data found in the request from user: {user_email}"
            )
            return jsonify({"success": False, "error": "Invalid Protobuf data"}), 400

        modify_food_request.ParseFromString(proto_data)
        time = modify_food_request.time
        percentage = modify_food_request.percentage
        logger.info(
            f"Extracted time and percentage from Protobuf for user {user_email}: time={time}, percentage={percentage}"
        )

        producer = create_producer()
        message_id = str(uuid.uuid4())
        message = {
            "key": message_id,
            "value": {"time": time, "user_email": user_email, "percentage": percentage},
        }
        produce_message(producer, topic="modify_food_record", message=message)
        logger.info(f"Sent message to Kafka for user {user_email}: {message}")

        logger.info(
            f"Waiting for modify confirmation for user {user_email} with message ID {message_id}"
        )

        # Get response from Redis using the background consumer service
        try:
            response = get_user_message_response(message_id, user_email, timeout=30)
            if response is not None:
                logger.info(
                    f"Retrieved modify confirmation for user {user_email}: {response}"
                )

                if response.get("error"):
                    logger.error(
                        f"Error in modify response for user {user_email}: {response.get('error')}"
                    )
                    modify_food_response.success = False
                    response_data = modify_food_response.SerializeToString()
                    return (
                        response_data,
                        500,
                        {"Content-Type": "application/grpc+proto"},
                    )

                modify_food_response.success = True
                response_data = modify_food_response.SerializeToString()
                return (
                    response_data,
                    200,
                    {"Content-Type": "application/grpc+proto"},
                )
            else:
                logger.warning(
                    f"Timeout waiting for modify confirmation for user {user_email} with message ID {message_id}"
                )
                modify_food_response.success = False
                response_data = modify_food_response.SerializeToString()
                return (
                    response_data,
                    500,
                    {"Content-Type": "application/grpc+proto"},
                )
        except Exception as e:
            logger.error(
                f"Failed to get modify confirmation for user {user_email}: {e}"
            )
            modify_food_response.success = False
            response_data = modify_food_response.SerializeToString()
            return (
                response_data,
                500,
                {"Content-Type": "application/grpc+proto"},
            )

    except Exception as e:
        logger.error(f"Error in modify_food_record for user {user_email}: {str(e)}")
        modify_food_response.success = False
        response_data = modify_food_response.SerializeToString()
        return response_data, 500, {"Content-Type": "application/grpc+proto"}


def manual_weight(request, user_email):
    manual_weight_response = manual_weight_pb2.ManualWeightResponse()
    manual_weight_request = manual_weight_pb2.ManualWeightRequest()
    try:
        proto_data = request.data
        if not proto_data:
            logger.error(
                f"No Protobuf data found in the request from user: {user_email}"
            )
            return jsonify({"success": False, "error": "Invalid Protobuf data"}), 400

        manual_weight_request.ParseFromString(proto_data)
        weight = manual_weight_request.weight
        user_email_from_proto = manual_weight_request.user_email
        logger.info(f"Extracted weight from Protobuf for user {user_email}: {weight}")

        producer = create_producer()
        message_id = str(uuid.uuid4())
        message = {
            "key": message_id,
            "value": {
                "user_email": user_email_from_proto,
                "weight": weight,
                "type": "weight_processing",
            },
        }
        produce_message(producer, topic="manual_weight", message=message)
        logger.info(
            f"Sent manual weight message to Kafka manual_weight topic for user {user_email}: {message}"
        )

        # Return success immediately after sending the message
        manual_weight_response.success = True
        response_data = manual_weight_response.SerializeToString()
        return (
            response_data,
            200,
            {"Content-Type": "application/grpc+proto"},
        )

    except Exception as e:
        logger.error(f"Error in manual_weight for user {user_email}: {str(e)}")
        manual_weight_response.success = False
        response_data = manual_weight_response.SerializeToString()
        return response_data, 500, {"Content-Type": "application/grpc+proto"}


def get_alcohol_latest(user_email):
    response = alcohol_pb2.GetAlcoholLatestResponse()
    try:
        producer = create_producer()
        message_id = str(uuid.uuid4())
        message = {"key": message_id, "value": {"user_email": user_email}}
        produce_message(producer, topic="get_alcohol_latest", message=message)

        # Wait for response
        kafka_response = get_user_message_response(message_id, user_email, timeout=30)
        if not kafka_response:
            return (
                response.SerializeToString(),
                500,
                {"Content-Type": "application/grpc+proto"},
            )

        alcohol = kafka_response.get("alcohol", {}) or {}
        response.today_summary.total_drinks = int(alcohol.get("total_drinks", 0))
        response.today_summary.total_calories = int(alcohol.get("total_calories", 0))
        for d in alcohol.get("drinks_of_day", []) or []:
            response.today_summary.drinks_of_day.append(d)
        return (
            response.SerializeToString(),
            200,
            {"Content-Type": "application/grpc+proto"},
        )
    except Exception as e:
        logger.error(f"Error in get_alcohol_latest for user {user_email}: {e}")
        return (
            response.SerializeToString(),
            500,
            {"Content-Type": "application/grpc+proto"},
        )


def get_alcohol_range(request, user_email):
    response = alcohol_pb2.GetAlcoholRangeResponse()
    req = alcohol_pb2.GetAlcoholRangeRequest()
    try:
        req.ParseFromString(request.data)
        start_date = req.start_date
        end_date = req.end_date

        producer = create_producer()
        message_id = str(uuid.uuid4())
        message = {
            "key": message_id,
            "value": {
                "user_email": user_email,
                "start_date": start_date,
                "end_date": end_date,
            },
        }
        produce_message(producer, topic="get_alcohol_range", message=message)

        kafka_response = get_user_message_response(message_id, user_email, timeout=30)
        if not kafka_response:
            return (
                response.SerializeToString(),
                500,
                {"Content-Type": "application/grpc+proto"},
            )

        for ev in kafka_response.get("events", []) or []:
            e = response.events.add()
            e.time = int(ev.get("time", 0))
            e.date = ev.get("date", "")
            e.drink_name = ev.get("drink_name", "")
            e.calories = int(ev.get("calories", 0))
            e.quantity = int(ev.get("quantity", 0))
        return (
            response.SerializeToString(),
            200,
            {"Content-Type": "application/grpc+proto"},
        )
    except Exception as e:
        logger.error(f"Error in get_alcohol_range for user {user_email}: {e}")
        return (
            response.SerializeToString(),
            500,
            {"Content-Type": "application/grpc+proto"},
        )
