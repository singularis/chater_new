import json
import logging
import uuid
from datetime import datetime

from common import get_prompt, json_to_plain_text
from kafka_consumer_service import get_user_message_response, get_message_response
from kafka_producer import create_producer, produce_message

from .proto import get_recomendation_pb2, today_food_pb2, custom_date_food_pb2

logger = logging.getLogger(__name__)


def eater_kafka_request(topic_send, topic_receive, payload, user_email, timeout_sec=30):
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
        response = get_user_message_response(message_id, user_email, timeout=timeout_sec)
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


def eater_get_custom_date_kafka(user_email, custom_date):
    payload = {
        "date": custom_date,
    }
    return eater_kafka_request("get_today_data_custom", "send_today_data_custom", payload, user_email)


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

        # Handle both old and new weight field names for backward compatibility
        lw = today_food.get("dishes", {}).get("latest_weight", {})
        if not lw:
            lw = today_food.get("dishes", {}).get("closest_weight", {})
        
        logger.info(
            f"Weight data for user {user_email}: {lw}, weight value: {lw.get('weight')}"
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


def eater_get_custom_date(request, user_email):
    try:
        proto_request = custom_date_food_pb2.CustomDateFoodRequest()
        proto_request.ParseFromString(request.data)
        
        custom_date = proto_request.date
        if not custom_date:
            logger.error(f"No date provided in custom date request for user {user_email}")
            return "No date provided", 400
            
        custom_food = eater_get_custom_date_kafka(user_email, custom_date)
        if not custom_food:
            raise ValueError(f"No data received from Kafka for user {user_email} and date {custom_date}")

        logger.info(
            f"Received custom_food from Kafka for user {user_email} and date {custom_date}: {custom_food}"
        )
        
        proto_message = custom_date_food_pb2.CustomDateFoodResponse()
        tf = custom_food.get("dishes", {}).get("total_for_day", {})
        logger.info(
            f"Total_for_day content for user {user_email} and date {custom_date}: {tf} | Types: { {k: type(v) for k, v in tf.items()} }"
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

        # Handle both old and new weight field names for backward compatibility
        lw = custom_food.get("dishes", {}).get("closest_weight", {})
        if not lw:
            lw = custom_food.get("dishes", {}).get("latest_weight", {})
        
        logger.info(
            f"Weight data for user {user_email} and date {custom_date}: {lw}, weight value: {lw.get('weight')}"
        )
        proto_message.person_weight = lw.get("weight", 0)

        dishes = custom_food.get("dishes", {}).get("dishes_today", [])
        for dish in dishes:
            logger.info(
                f"Processing dish for user {user_email}: {dish} | "
                f"Types: {{ { {k: type(v) for k, v in dish.items()} } }}"
            )
            dish_proto = proto_message.dishes_for_date.add()
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
            f"Successfully processed custom date message for user {user_email} and date {custom_date}: {custom_food}"
        )
        return proto_data, 200, {"Content-Type": "application/protobuf"}

    except Exception as e:
        logger.error(f"Exception in eater_get_custom_date for user {user_email}: {e}")
        logger.error(
            f"Problematic message for user {user_email}: {custom_food if 'custom_food' in locals() else 'None'}"
        )
        return "Failed", 500


def eater_auth_token(request):
    """Handle authentication token request"""
    logger.info("=== ENTERING eater_auth_token function ===")
    try:
        import json
        from flask import jsonify
        
        # Parse the request JSON
        request_data = request.get_json()
        if not request_data:
            logger.error("No JSON data in auth request")
            return jsonify({"error": "invalid_request", "message": "No JSON data provided"}), 400
        
        # Extract required fields
        provider = request_data.get("provider")
        id_token = request_data.get("idToken")
        email = request_data.get("email")
        name = request_data.get("name")
        profile_picture_url = request_data.get("profilePictureURL")
        
        # Validate required fields
        if not provider or not id_token or not email:
            logger.error("Missing required fields in auth request")
            return jsonify({
                "error": "invalid_request", 
                "message": "Missing required fields: provider, idToken, email"
            }), 400
        
        if provider not in ["google", "apple"]:
            logger.error(f"Invalid provider: {provider}")
            return jsonify({
                "error": "invalid_provider",
                "message": "Provider must be google or apple"
            }), 400
        
        # Create payload for Kafka message
        payload = {
            "provider": provider,
            "idToken": id_token,
            "email": email,
            "name": name,
            "profilePictureURL": profile_picture_url
        }
        
        # Use the standard eater_kafka_request function like other endpoints
        logger.info(f"Sending auth request to Kafka for email: {email}")
        
        # Create a temporary user email since this is before authentication
        temp_user_email = email  # Use the email from the request as user identifier
        
        # Send to Kafka using the standard pattern
        message_id = str(uuid.uuid4())
        message = {"key": message_id, "value": {**payload, "user_email": temp_user_email}}
        
        logger.info(f"AUTH DEBUG - Message created in auth function: {message}")
        logger.info(f"AUTH DEBUG - temp_user_email: {temp_user_email}")
        logger.info(f"AUTH DEBUG - payload: {payload}")
        
        producer = create_producer()
        produce_message(producer, topic="auth_requires_token", message=message)
        
        logger.info(f"Waiting for auth response from topic add_auth_token with message ID {message_id}")
        
        # Get response from Redis using the background consumer service
        try:
            response = get_message_response(message_id, timeout=30)
            if response is not None:
                logger.info(f"Retrieved auth response for email {email}: {response}")
                
                if response.get("error"):
                    logger.error(f"Error in auth response for email {email}: {response.get('error')}")
                    return jsonify({
                        "error": response.get("error"),
                        "message": response.get("message", "Authentication failed")
                    }), 401
                
                # Return successful response
                return jsonify({
                    "token": response.get("token"),
                    "expiresIn": response.get("expiresIn", 86400),
                    "userEmail": response.get("userEmail", email),
                    "userName": response.get("userName", name),
                    "profilePictureURL": response.get("profilePictureURL", profile_picture_url)
                }), 200
            else:
                logger.warning(f"Timeout waiting for auth response with message ID {message_id}")
                return jsonify({
                    "error": "timeout",
                    "message": "Authentication request timed out"
                }), 500
        except Exception as e:
            logger.error(f"Failed to get auth message response: {e}")
            return jsonify({
                "error": "internal_error",
                "message": "Failed to process authentication request"
            }), 500
            
    except Exception as e:
        logger.error(f"Exception in eater_auth_token: {e}")
        return jsonify({
            "error": "internal_error",
            "message": "Authentication service temporarily unavailable"
        }), 500


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
            "get_recommendation", "gemini-response", payload, user_email, timeout_sec=90
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
