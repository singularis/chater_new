import json
import logging
import uuid
from datetime import datetime

from common import get_prompt, json_to_plain_text
from kafka_consumer import consume_messages, create_consumer
from kafka_producer import create_producer, produce_message

from .proto import get_recomendation_pb2, today_food_pb2

logger = logging.getLogger(__name__)


def eater_kafka_request(topic_send, topic_receive, payload):
    producer = create_producer()
    logger.info(f"Sending request to topic {topic_send}")
    message = {
        "key": str(uuid.uuid4()),
        "value": payload,
    }
    produce_message(producer, topic=topic_send, message=message)

    logger.info(f"Listening for response on topic {topic_receive}")
    consumer = create_consumer([topic_receive])
    for message in consume_messages(consumer):
        try:
            value = message.value().decode("utf-8")
            value_dict = json.loads(value)
            consumer.commit(message)
            return value_dict.get("value")
        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            return None


def eater_get_today_kafka():
    payload = {
        "date": datetime.now().strftime("%d-%m-%Y"),
    }
    return eater_kafka_request("get_today_data", "send_today_data", payload)


def eater_get_today():
    try:
        today_food = eater_get_today_kafka()
        if today_food is None:
            raise ValueError("No data received from Kafka")

        proto_message = today_food_pb2.TodayFood()
        proto_message.total_for_day.total_avg_weight = today_food["total_for_day"][
            "total_avg_weight"
        ]
        proto_message.total_for_day.total_calories = today_food["total_for_day"][
            "total_calories"
        ]
        proto_message.total_for_day.contains.carbohydrates = today_food[
            "total_for_day"
        ]["contains"]["carbohydrates"]
        proto_message.total_for_day.contains.fats = today_food["total_for_day"][
            "contains"
        ]["fats"]
        proto_message.total_for_day.contains.proteins = today_food["total_for_day"][
            "contains"
        ]["proteins"]
        proto_message.total_for_day.contains.sugar = today_food["total_for_day"][
            "contains"
        ]["sugar"]
        proto_message.person_weight = today_food["latest_weight"]["weight"]
        for dish in today_food["dishes_today"]:
            dish_proto = proto_message.dishes_today.add()
            dish_proto.time = dish["time"]
            dish_proto.dish_name = dish["dish_name"]
            dish_proto.estimated_avg_calories = dish["estimated_avg_calories"]
            dish_proto.total_avg_weight = dish["total_avg_weight"]
            dish_proto.ingredients.extend(dish["ingredients"])
        proto_data = proto_message.SerializeToString()
        return proto_data, 200, {"Content-Type": "application/protobuf"}
    except Exception as e:
        logger.error(f"Exception: {e}")
        return "Failed", 500


def get_recommendation(request):
    try:
        proto_request = get_recomendation_pb2.RecommendationRequest()
        proto_request.ParseFromString(request.data)

        days = proto_request.days
        prompt = get_prompt("get_recommendation")
        payload = {
            "days": days,
            "prompt": prompt,
            "type_of_processing": "get_recommendation",
        }
        recommendation_data = eater_kafka_request(
            "get_recommendation", "gemini-response", payload
        )
        logger.info(f"recommendation_data {recommendation_data}")
        if recommendation_data is None:
            raise ValueError("No recommendation received from Kafka")
        plain_text = json_to_plain_text(recommendation_data)
        logger.info(f"plain_text {plain_text}")
        proto_response = get_recomendation_pb2.RecommendationResponse()
        proto_response.recommendation = plain_text
        response_data = proto_response.SerializeToString()
        return response_data, 200, {"Content-Type": "application/protobuf"}
    except Exception as e:
        logger.error(f"Exception: {e}")
        return "Failed", 500
