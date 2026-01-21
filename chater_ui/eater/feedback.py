import logging
import uuid

from flask import jsonify, request
from kafka_producer import KafkaDispatchError, send_kafka_message

from .proto import feedback_pb2

logger = logging.getLogger(__name__)


def submit_feedback_request(user_email):
    """Handle feedback submission request in protobuf format."""
    feedback_response = feedback_pb2.FeedbackResponse()
    feedback_request = feedback_pb2.FeedbackRequest()

    try:
        # Get protobuf data from request
        proto_data = request.data
        if not proto_data:
            logger.error(
                "No Protobuf data found in the request from user %s", user_email
            )
            return jsonify({"success": False, "error": "Invalid Protobuf data"}), 400

        # Parse protobuf request
        feedback_request.ParseFromString(proto_data)

        # Extract fields from protobuf
        time = feedback_request.time
        user_email_from_proto = feedback_request.userEmail
        feedback_text = feedback_request.feedback

        logger.debug(
            "Extracted feedback protobuf for user %s: time=%s", user_email, time
        )

        # Validate feedback
        if not feedback_text.strip():
            logger.warning("Empty feedback from user %s", user_email)
            feedback_response.success = False
            response_data = feedback_response.SerializeToString()
            return (
                response_data,
                400,
                {"Content-Type": "application/grpc+proto"},
            )

        # Create producer and message for Kafka
        message_key = str(uuid.uuid4())

        kafka_message = {
            "time": time,
            "user_email": user_email_from_proto,
            "feedback": feedback_text,
        }

        # Send message to feedback topic
        try:
            send_kafka_message(
                "feedback",
                value=kafka_message,
                key=message_key,
            )
        except KafkaDispatchError as kafka_error:
            logger.error(
                "Failed to send feedback for user %s: %s", user_email, kafka_error
            )
            feedback_response.success = False
            response_data = feedback_response.SerializeToString()
            return (
                response_data,
                kafka_error.status_code,
                {"Content-Type": "application/grpc+proto"},
            )
        except Exception as exc:
            logger.exception(
                "Unexpected error while sending feedback for user %s", user_email
            )
            feedback_response.success = False
            response_data = feedback_response.SerializeToString()
            return (
                response_data,
                500,
                {"Content-Type": "application/grpc+proto"},
            )

        logger.info("Feedback submitted for user %s", user_email)

        # Create successful protobuf response
        feedback_response.success = True
        response_data = feedback_response.SerializeToString()
        return (
            response_data,
            200,
            {"Content-Type": "application/grpc+proto"},
        )

    except Exception as exc:
        logger.exception("Error submitting feedback for user %s", user_email)
        feedback_response.success = False
        response_data = feedback_response.SerializeToString()
        return (
            response_data,
            500,
            {"Content-Type": "application/grpc+proto"},
        )
