import base64
import io
import json
import logging
import os
import re
from datetime import datetime, timedelta
from functools import wraps

import jwt
import yaml
from flask import flash, jsonify, redirect, request, url_for
from PIL import Image

log = logging.getLogger("main")
SECRET_KEY = str(os.getenv("EATER_SECRET_KEY"))
PROMPT_FILE = "eater/prompt.yaml"


def before_request(session, app, SESSION_LIFETIME):
    session.permanent = True
    app.permanent_session_lifetime = timedelta(hours=SESSION_LIFETIME)
    session.modified = True
    if "logged_in" in session:
        last_activity_str = session.get("last_activity", None)
        if last_activity_str:
            if isinstance(last_activity_str, datetime):
                last_activity_str = last_activity_str.strftime("%Y-%m-%d %H:%M:%S")
            last_activity = datetime.strptime(last_activity_str, "%Y-%m-%d %H:%M:%S")
            if datetime.now() - last_activity > timedelta(hours=SESSION_LIFETIME):
                session.pop("logged_in", None)
                logging.info("logged out due to inactivity: %s", last_activity_str)
                flash("You have been logged out due to inactivity.")
                return redirect(url_for("chater_login"))
        session["last_activity"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def chater_clear(session):
    if "logged_in" in session:
        session["responses"] = []
        session["context"] = None
        flash("Responses cleared successfully")
        referrer = request.referrer
        if referrer:
            return redirect(referrer)
        else:
            return redirect(url_for("chater"))
    else:
        logging.warning("Unauthorized clear attempt")
        flash("You need to log in to perform this action")
        return redirect(url_for("chater_login"))


def token_required(f):
    @wraps(f)  # This preserves the original function's metadata
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            logging.debug("Authorization header is missing")
            return jsonify({"message": "Token is missing"}), 401
        if not auth_header.startswith("Bearer "):
            logging.debug("Authorization header is invalid: %s", auth_header)
            return jsonify({"message": "Invalid token format"}), 401
        try:
            token = auth_header.split(" ")[1]
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            logging.debug("Decoded token subject: %s", decoded_token.get("sub"))
        except jwt.ExpiredSignatureError:
            logging.debug("Token has expired")
            return jsonify({"message": "Token has expired"}), 401
        except jwt.InvalidTokenError as e:
            logging.debug("Invalid token: %s", str(e))
            return jsonify({"message": "Invalid token"}), 401

        return f(*args, **kwargs)

    return wrapper


def get_prompt(key):
    try:
        logging.debug(f"Attempting to open the file {PROMPT_FILE}.")
        with open(PROMPT_FILE, "r") as file:
            data = yaml.safe_load(file)
            logging.info(f"Successfully loaded data from {PROMPT_FILE}.")
        value = data.get(key)
        if value is not None:
            logging.info(f"Key '{key}' found in the YAML file. Value: {value}")
            return value
        else:
            logging.error(f"Key '{key}' is not defined in the YAML file.")
            raise ValueError(f"Key '{key}' is not defined in the YAML file.")
    except FileNotFoundError:
        logging.critical(f"The file {PROMPT_FILE} was not found.")
        raise FileNotFoundError(f"Error: The file {PROMPT_FILE} was not found.")
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML file: {e}")
        raise ValueError(f"Error parsing YAML file: {e}")
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")
        raise RuntimeError(f"An unexpected error occurred: {e}")


def resize_image(image_data, max_size=(1024, 1024)):
    try:
        image = Image.open(io.BytesIO(image_data))

        image.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Save the resized image back to binary
        output = io.BytesIO()
        image.save(output, format=image.format)
        return output.getvalue()
    except Exception as e:
        logging.error(f"Failed to resize image: {str(e)}")
        raise


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


import json


def json_to_plain_text(json_data):
    if isinstance(json_data, str):
        cleaned_data = json_data.strip()
        if cleaned_data.startswith("```json"):
            cleaned_data = cleaned_data[len("```json") :].strip("`").strip()
        elif cleaned_data.startswith("json"):
            cleaned_data = cleaned_data[len("json") :].strip()

        try:
            json_data = json.loads(cleaned_data)
        except json.JSONDecodeError:
            return "Invalid JSON input."

    output_text = ""

    if "foods_to_reduce_or_avoid" in json_data:
        output_text += "Foods to Reduce or Avoid:\n\n"
        for food in json_data["foods_to_reduce_or_avoid"]:
            dish_name = food.get("dish_name", "Unnamed Dish")
            reason = food.get("reason", "")
            output_text += f"- {dish_name}: {reason}\n"
            output_text += "\n"
        output_text += "\n"

    if "healthier_foods" in json_data:
        output_text += "Healthier Food Options:\n\n"
        for food in json_data["healthier_foods"]:
            dish_name = food.get("dish_name", "Unnamed Dish")
            reason = food.get("reason", "")
            output_text += f"- {dish_name}: {reason}\n"
            output_text += "\n"
        output_text += "\n"

    if "general_recommendations" in json_data:
        output_text += "General Recommendations:\n\n"
        if isinstance(json_data["general_recommendations"], dict):
            for key, value in json_data["general_recommendations"].items():
                output_text += f"- {value}\n"
        else:
            output_text += f"{json_data['general_recommendations']}\n"
        output_text += "\n"

    for key, value in json_data.items():
        if key not in [
            "general_recommendations",
            "healthier_foods",
            "foods_to_reduce_or_avoid",
        ]:
            display_key = key.replace("_", " ").title()
            if isinstance(value, list):
                output_text += f"{display_key}:\n"
                for item in value:
                    output_text += f"- {item}\n"
                output_text += "\n"
            elif isinstance(value, str):
                output_text += f"{display_key}:\n{value}\n\n"
            elif isinstance(value, dict):
                output_text += f"{display_key}:\n"
                for sub_key, sub_value in value.items():
                    output_text += (
                        f"- {sub_key.replace('_', ' ').title()}: {sub_value}\n"
                    )
                output_text += "\n"

    return output_text
