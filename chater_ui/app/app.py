import logging
import os
import atexit
import time

import context
import redis
from common import (before_request, chater_clear, generate_session_secret,
                    token_required, rate_limit_required)
from flask import Flask, jsonify, render_template, request, session, redirect, url_for, flash, g
from flask_cors import CORS
from flask_session import Session
from google_ops import create_google_blueprint, g_login
from gphoto import gphoto, gphoto_proxy
from kafka_consumer_service import start_kafka_consumer_service, stop_kafka_consumer_service
from logging_config import setup_logging
from login import login, logout
from werkzeug.middleware.proxy_fix import ProxyFix

from chater import chater as chater_ui
from eater.eater import (delete_food_record, eater_photo, eater_today, eater_custom_date,
                         get_recommendations, modify_food_record_data, eater_auth_request, manual_weight_record,
                         alcohol_latest, alcohol_range, set_language)
from eater.feedback import submit_feedback_request
from eater_admin import eater_admin_request, eater_admin_proxy
from .metrics import metrics_endpoint, record_http_metrics, track_eater_operation

setup_logging("app.log")
logger = logging.getLogger(__name__)

# Enable debug logging for personal development
if os.getenv("FLASK_DEBUG", "true").lower() == "true":
    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger("werkzeug").setLevel(logging.DEBUG)
    logging.getLogger("flask").setLevel(logging.DEBUG)
    logger.info("Debug logging enabled for personal development")

redis_client = redis.StrictRedis(host=os.getenv("REDIS_ENDPOINT"), port=6379, db=0)
app = Flask(__name__, static_url_path="/chater/static")

# Personal development configuration - secure but with debug logging
app.config.update(
    SECRET_KEY=os.getenv("SECRET_KEY", generate_session_secret()),
    SESSION_TYPE="redis",
    SESSION_REDIS=redis_client,
    SESSION_PERMANENT=False,
    SESSION_USE_SIGNER=True,
    SESSION_KEY_PREFIX="chater_ui:",
    # Security headers for personal app
    SESSION_COOKIE_SECURE=True if os.getenv("HTTPS_ENABLED", "false").lower() == "true" else False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    # Enable debug logging for personal development
    DEBUG=os.getenv("FLASK_DEBUG", "true").lower() == "true",
    TESTING=False
)

Session(app)

picFolder = "/app/app/static/pics"
SESSION_LIFETIME = int(os.getenv("SESSION_LIFETIME"))
ALLOWED_EMAILS = os.getenv("ALLOWED_EMAILS", "").split(",")

google_bp = create_google_blueprint()
app.register_blueprint(google_bp, url_prefix="/google_login")
CORS(app)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

# Start the background Kafka consumer service
logger.info("Starting Kafka Consumer Service...")
start_kafka_consumer_service()

# Register cleanup function for graceful shutdown
atexit.register(stop_kafka_consumer_service)


@app.before_request
def before():
    if request.path != "/metrics":
        g._http_request_start_time = time.time()
    return before_request(session=session, app=app, SESSION_LIFETIME=SESSION_LIFETIME)



@app.after_request
def metrics_after_request(response):
    try:
        if request.path != "/metrics":
            start_time = getattr(g, "_http_request_start_time", time.time())
            endpoint_label = request.endpoint or request.path
            record_http_metrics(start_time=start_time, endpoint=endpoint_label, status=response.status_code)
    finally:
        return response


@app.teardown_request
def metrics_teardown_request(exc):
    if exc is not None and request and request.path != "/metrics":
        start_time = getattr(g, "_http_request_start_time", time.time())
        endpoint_label = request.endpoint or request.path
        record_http_metrics(start_time=start_time, endpoint=endpoint_label, status=500)


@app.route("/chater_login", methods=["GET", "POST"])
def chater_login():
    return login(session=session)


@app.route("/google_login")
def google_login():
    return g_login(session=session, ALLOWED_EMAILS=ALLOWED_EMAILS)


@app.route("/chater", methods=["GET", "POST"])
def chater():
    return chater_ui(session, target="chater")


@app.route("/chamini", methods=["GET", "POST"])
def chamini():
    return chater_ui(session, target="chamini")


@app.route("/gempt", methods=["GET", "POST"])
def gempt():
    return chater_ui(session, target="gempt")


@app.route("/chater_clear_responses", methods=["GET"])
def chater_clear_responses():
    return chater_clear(session=session)


@app.route("/chater_logout")
def chater_logout():
    return logout(session=session)


@app.route("/chater_wait")
def chater_wait():
    logger.warning("Waiting for next chater_login attempt")
    return render_template("wait.html")


@app.route("/gphoto", methods=["GET"])
def gphoto_ui():
    return gphoto(session, picFolder)


@app.route("/gphoto_proxy/<path:resource_path>", methods=["GET"])
def gphoto_proxy_route(resource_path):
    return gphoto_proxy(resource_path)


@app.route("/toggle-switch", methods=["POST"])
def toggle_switch():
    return context.context_switch(session)


@app.route("/get-switch-state", methods=["GET"])
def get_switch_state():
    return context.use_switch_state(session)


@app.route("/eater_test", methods=["GET"])
@token_required
def eater(user_email):
    return jsonify({"message": f"Eater endpoint granted for user: {user_email}!"})


@app.route("/eater_receive_photo", methods=["POST"])
@track_eater_operation("receive_photo")
@token_required
@rate_limit_required
def eater_receive_photo(user_email):
    return eater_photo(user_email=user_email)


@app.route("/eater_get_today", methods=["GET"])
@track_eater_operation("get_today")
@token_required
def eater_get_today(user_email):
    return eater_today(user_email=user_email)


@app.route("/get_food_custom_date", methods=["POST"])
@track_eater_operation("get_food_custom_date")
@token_required
def get_food_custom_date(user_email):
    return eater_custom_date(request=request, user_email=user_email)


@app.route("/delete_food", methods=["POST"])
@track_eater_operation("delete_food")
@token_required
def delete_food(user_email):
    return delete_food_record(request=request, user_email=user_email)


@app.route("/modify_food_record", methods=["POST"])
@track_eater_operation("modify_food_record")
@token_required
def modify_food(user_email):
    return modify_food_record_data(request=request, user_email=user_email)


@app.route("/get_recommendation", methods=["POST"])
@track_eater_operation("get_recommendation")
@token_required
@rate_limit_required
def recommendations(user_email):
    recommendation = get_recommendations(request=request, user_email=user_email)
    return recommendation


@app.route("/eater_auth", methods=["POST"])
@track_eater_operation("eater_auth")
def eater_auth():
    return eater_auth_request(request=request)


@app.route("/manual_weight", methods=["POST"])
@track_eater_operation("manual_weight")
@token_required
def manual_weight(user_email):
    return manual_weight_record(request=request, user_email=user_email)
@app.route("/alcohol_latest", methods=["GET"])
@track_eater_operation("alcohol_latest")
@token_required
def get_alcohol_latest_route(user_email):
    return alcohol_latest(user_email=user_email)


@app.route("/alcohol_range", methods=["POST"])
@track_eater_operation("alcohol_range")
@token_required
def get_alcohol_range_route(user_email):
    return alcohol_range(request=request, user_email=user_email)



@app.route("/feedback", methods=["POST"])
@track_eater_operation("submit_feedback")
@token_required
def submit_feedback(user_email):
    return submit_feedback_request(user_email=user_email)


@app.route("/eater_admin", methods=["GET", "POST"])
def eater_admin():
    return eater_admin_request(session)


@app.route("/eater_admin_proxy/<path:resource_path>", methods=["GET"])
def eater_admin_proxy_route(resource_path):
    return eater_admin_proxy(resource_path)


@app.route("/set_language", methods=["POST"])
@track_eater_operation("set_language")
@token_required
def set_language_route(user_email):
    return set_language(request=request, user_email=user_email)


@app.route("/metrics")
def metrics():
    return metrics_endpoint()


if __name__ == "__main__":
    # Local development with debug logging enabled
    logging.getLogger("werkzeug").setLevel(logging.DEBUG)
    logging.getLogger().setLevel(logging.DEBUG)
    app.run(host="0.0.0.0", debug=True)
