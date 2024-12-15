import json
import logging
import uuid
from datetime import datetime

from kafka_consumer import consume_messages, create_consumer
from kafka_producer import create_producer, produce_message

from .proto import today_food_pb2

logger = logging.getLogger(__name__)


def eater_get_today_kafka():
    producer = create_producer()
    logger.info(f"Received request to get food")
    message = {
        "key": str(uuid.uuid4()),
        "value": {
            "date": datetime.now().strftime("%d-%m-%Y"),
        },
    }
    produce_message(producer, topic="get_today_data", message=message)
    logger.info(f"Listening Kafka to get today")
    consumer = create_consumer(["send_today_data"])
    for message in consume_messages(consumer):
        try:
            value = message.value().decode("utf-8")
            value_dict = json.loads(value)
            consumer.commit(message)
            return value_dict.get("value")
        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            return "Timeout"


def eater_get_today():
    try:
        today_food = eater_get_today_kafka()
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
        logger.info(f"Exception {e}")
        return "Failed", 500
