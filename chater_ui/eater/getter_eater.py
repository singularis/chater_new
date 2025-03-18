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
        if not today_food:
            raise ValueError("No data received from Kafka")

        logger.info(f"Received today_food from Kafka: {today_food}")
        proto_message = today_food_pb2.TodayFood()
        tf = today_food.get("total_for_day", {})
        logger.info(
            f"Total_for_day content: {tf} | Types: { {k: type(v) for k, v in tf.items()} }"
        )
        total_avg_weight = tf.get("total_avg_weight", 0)
        logger.info(
            f"Assigning total_avg_weight: {total_avg_weight} (type: {type(total_avg_weight)})"
        )
        proto_message.total_for_day.total_avg_weight = int(total_avg_weight)
        total_calories = tf.get("total_calories", 0)
        logger.info(
            f"Assigning total_calories: {total_calories} (type: {type(total_calories)})"
        )
        proto_message.total_for_day.total_calories = total_calories
        contains_data = tf.get("contains", {})
        if isinstance(contains_data, list):
            logger.warning(
                f"'contains' is a list instead of dict: {contains_data}. Defaulting to empty."
            )
            contains_data = {}
        elif not isinstance(contains_data, dict):
            logger.warning(
                f"'contains' is neither dict nor list: {contains_data}. Defaulting to empty."
            )
            contains_data = {}

        proto_message.total_for_day.contains.carbohydrates = int(
            contains_data.get("carbohydrates", 0)
        )
        proto_message.total_for_day.contains.fats = int(contains_data.get("fats", 0))
        proto_message.total_for_day.contains.proteins = int(
            contains_data.get("proteins", 0)
        )
        proto_message.total_for_day.contains.sugar = int(contains_data.get("sugar", 0))

        lw = today_food.get("latest_weight", {})
        proto_message.person_weight = lw.get("weight", 0)

        dishes = today_food.get("dishes_today", [])
        for dish in dishes:
            logger.info(
                f"Processing dish: {dish} | "
                f"Types: {{ { {k: type(v) for k, v in dish.items()} } }}"
            )
            dish_proto = proto_message.dishes_today.add()
            dish_proto.time = dish.get("time", 0)
            dish_proto.dish_name = dish.get("dish_name", "")
            dish_proto.estimated_avg_calories = dish.get("estimated_avg_calories", 0)
            dish_proto.total_avg_weight = int(dish.get("total_avg_weight", 0))
            ingredients = dish.get("ingredients", [])
            if not isinstance(ingredients, list):
                logger.warning(
                    f"'ingredients' is not a list: {ingredients}. Converting to empty list."
                )
                ingredients = []
            dish_proto.ingredients.extend(ingredients)

        proto_data = proto_message.SerializeToString()
        logger.info(f"Successfully processed message: {today_food}")
        return proto_data, 200, {"Content-Type": "application/protobuf"}

    except Exception as e:
        logger.error(f"Exception in eater_get_today: {e}")
        logger.error(
            f"Problematic message: {today_food if 'today_food' in locals() else 'None'}"
        )
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
