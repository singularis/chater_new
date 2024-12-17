import logging
import os

import context
from common import before_request, chater_clear, token_required
from flask import Flask, jsonify, render_template, request, session
from flask_cors import CORS
from google_ops import create_google_blueprint, g_login
from gphoto import gphoto
from logging_config import setup_logging
from login import login, logout
from werkzeug.middleware.proxy_fix import ProxyFix

from chater import chater as chater_ui
from eater.eater import delete_food_record, eater_photo, eater_today, get_recommendations

setup_logging("app.log")
logger = logging.getLogger(__name__)

app = Flask(__name__, static_url_path="/chater/static")
app.secret_key = os.getenv("SECRET_KEY")

picFolder = "/app/app/static/pics"
SESSION_LIFETIME = int(os.getenv("SESSION_LIFETIME"))
ALLOWED_EMAILS = os.getenv("ALLOWED_EMAILS", "").split(",")

google_bp = create_google_blueprint()
app.register_blueprint(google_bp, url_prefix="/google_login")
CORS(app)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)


@app.before_request
def before():
    return before_request(session=session, app=app, SESSION_LIFETIME=SESSION_LIFETIME)


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


@app.route("/toggle-switch", methods=["POST"])
def toggle_switch():
    return context.context_switch(session)


@app.route("/get-switch-state", methods=["GET"])
def get_switch_state():
    return context.use_switch_state(session)


@app.route("/eater_test", methods=["GET"])
@token_required
def eater():
    return jsonify({"message": "Eater endpoint granted!"})


@app.route("/eater_receive_photo", methods=["POST"])
@token_required
def eater_receive_photo():
    return eater_photo()


@app.route("/eater_get_today", methods=["GET"])
@token_required
def eater_get_today():
    return eater_today()


@app.route("/delete_food", methods=["POST"])
@token_required
def delete_food():
    return delete_food_record(request=request)

@app.route("/get_recommendation", methods=["POST"])
@token_required
def recommendations():
    recommendation = get_recommendations(request=request)
    return recommendation


if __name__ == "__main__":
    logging.getLogger("werkzeug").setLevel(logging.INFO)
    app.run(host="0.0.0.0")
