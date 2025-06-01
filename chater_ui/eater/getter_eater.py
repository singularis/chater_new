import json
import logging
import uuid
from datetime import datetime

from common import get_prompt, json_to_plain_text
from kafka_consumer_service import get_user_message_response
from kafka_producer import create_producer, produce_message

from .proto import get_recomendation_pb2, today_food_pb2

logger = logging.getLogger(__name__)


def eater_kafka_request(topic_send, topic_receive, payload, user_email):
    producer = create_producer()
    message_id = str(uuid.uuid4())
    logger.info(f"Sending request to topic {topic_send} for user {user_email}")
    message = {"key": message_id, "value": {**payload, "user_email": user_email}}
    produce_message(producer, topic=topic_send, message=message)

    logger.info(
        f"Waiting for response from topic {topic_receive} for user {user_email} with message ID {message_id}"
    )
    
    # Get response from Redis using the background consumer service
    try:
        response = get_user_message_response(message_id, user_email, timeout=30)
        if response is not None:
            logger.info(f"Retrieved response for user {user_email}: {response}")
            
            if response.get("error"):
                logger.error(f"Error in response for user {user_email}: {response.get('error')}")
                return None
            
            return response
        else:
            logger.warning(f"Timeout waiting for response for user {user_email} with message ID {message_id}")
            return None
    except Exception as e:
        logger.error(f"Failed to get message response for user {user_email}: {e}")
        return None


def eater_get_today_kafka(user_email):
    payload = {
        "date": datetime.now().strftime("%d-%m-%Y"),
    }
    return eater_kafka_request("get_today_data", "send_today_data", payload, user_email)


def eater_get_today(user_email):
    try:
        today_food = eater_get_today_kafka(user_email)
        if not today_food:
            raise ValueError(f"No data received from Kafka for user {user_email}")

        logger.info(
            f"Received today_food from Kafka for user {user_email}: {today_food}"
        )
        proto_message = today_food_pb2.TodayFood()
        tf = today_food.get("dishes", {}).get("total_for_day", {})
        logger.info(
            f"Total_for_day content for user {user_email}: {tf} | Types: { {k: type(v) for k, v in tf.items()} }"
        )
        total_avg_weight = tf.get("total_avg_weight", 0)
        logger.info(
            f"Assigning total_avg_weight for user {user_email}: {total_avg_weight} (type: {type(total_avg_weight)})"
        )
        proto_message.total_for_day.total_avg_weight = int(total_avg_weight)
        total_calories = tf.get("total_calories", 0)
        logger.info(
            f"Assigning total_calories for user {user_email}: {total_calories} (type: {type(total_calories)})"
        )
        proto_message.total_for_day.total_calories = total_calories
        contains_data = tf.get("contains", {})
        if isinstance(contains_data, list):
            logger.warning(
                f"'contains' is a list instead of dict for user {user_email}: {contains_data}. Defaulting to empty."
            )
            contains_data = {}
        elif not isinstance(contains_data, dict):
            logger.warning(
                f"'contains' is neither dict nor list for user {user_email}: {contains_data}. Defaulting to empty."
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

        lw = today_food.get("dishes", {}).get("latest_weight", {})
        logger.info(
            f"Latest weight for user {user_email}: {lw}, lw.get('weight'): {lw.get('weight')}"
        )
        proto_message.person_weight = lw.get("weight", 0)

        dishes = today_food.get("dishes", {}).get("dishes_today", [])
        for dish in dishes:
            logger.info(
                f"Processing dish for user {user_email}: {dish} | "
                f"Types: {{ { {k: type(v) for k, v in dish.items()} } }}"
            )
            dish_proto = proto_message.dishes_today.add()
            dish_proto.time = dish.get("time", 0)
            dish_proto.dish_name = dish.get("dish_name", "")
            dish_proto.estimated_avg_calories = dish.get("estimated_avg_calories", 0)
            dish_proto.total_avg_weight = int(dish.get("total_avg_weight", 0))

            ingredients = dish.get("ingredients", [])
            logger.info(
                f"Raw ingredients for dish {dish.get('dish_name')}: {ingredients}"
            )
            if not isinstance(ingredients, list):
                logger.warning(
                    f"'ingredients' is not a list for user {user_email}: {ingredients}. Converting to empty list."
                )
                ingredients = []
            dish_proto.ingredients.extend(ingredients)
            logger.info(f"Processed dish proto: {dish_proto}")

        proto_data = proto_message.SerializeToString()
        logger.info(
            f"Successfully processed message for user {user_email}: {today_food}"
        )
        return proto_data, 200, {"Content-Type": "application/protobuf"}

    except Exception as e:
        logger.error(f"Exception in eater_get_today for user {user_email}: {e}")
        logger.error(
            f"Problematic message for user {user_email}: {today_food if 'today_food' in locals() else 'None'}"
        )
        return "Failed", 500


def get_recommendation(request, user_email):
    try:
        proto_request = get_recomendation_pb2.RecommendationRequest()
        proto_request.ParseFromString(request.data)

        days = proto_request.days
        prompt = get_prompt("get_recommendation")
        message_id = str(uuid.uuid4())
        payload = {
            "days": days,
            "prompt": prompt,
            "type_of_processing": "get_recommendation",
        }

        recommendation_data = eater_kafka_request(
            "get_recommendation", "gemini-response", payload, user_email
        )
        logger.info(f"recommendation_data for user {user_email}: {recommendation_data}")
        if recommendation_data is None:
            raise ValueError(
                f"No recommendation received from Kafka for user {user_email}"
            )
        plain_text = json_to_plain_text(recommendation_data)
        logger.info(f"plain_text for user {user_email}: {plain_text}")
        proto_response = get_recomendation_pb2.RecommendationResponse()
        proto_response.recommendation = plain_text
        response_data = proto_response.SerializeToString()
        return response_data, 200, {"Content-Type": "application/protobuf"}
    except Exception as e:
        logger.error(f"Exception for user {user_email}: {e}")
        return "Failed", 500
