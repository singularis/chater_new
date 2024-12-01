from kafka_producer import produce_message, create_producer
import logging
from .proto import delete_food_pb2
from flask import jsonify
import uuid

logger = logging.getLogger(__name__)

def delete_food(request):
    delete_food_response = delete_food_pb2.DeleteFoodResponse()
    delete_food_request = delete_food_pb2.DeleteFoodRequest()
    try:
        proto_data = request.data
        if not proto_data:
            logger.error("No Protobuf data found in the request")
            return jsonify({"success": False, "error": "Invalid Protobuf data"}), 400
        delete_food_request.ParseFromString(proto_data)
        time = delete_food_request.time
        logger.info(f"Extracted time from Protobuf: {time}")
        producer = create_producer()
        message = {
            "key":  str(uuid.uuid4()),
            "value": time,
        }
        produce_message(producer, topic="delete_food", message=message)
        logger.info(f"Sent message to Kafka: {message}")
        delete_food_response.success = True
        response_data = delete_food_response.SerializeToString()
        return response_data, 200, {'Content-Type': 'application/grpc+proto'}
    except Exception as e:
        logger.error(f"Error in delete_food: {str(e)}")
        delete_food_response.success = False
        response_data = delete_food_response.SerializeToString()
        return response_data, 500, {'Content-Type': 'application/grpc+proto'}
