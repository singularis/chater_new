from flask import (
    Flask,
    render_template,
    session,
    redirect,
    url_for,
    flash,
    request,
)
from flask_dance.contrib.google import make_google_blueprint, google
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import logging
from gphoto import gphoto
from chater import chater as chater_ui
from common import before_request, chater_clear
from login import login, logout
from google_ops import g_login

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = Flask(__name__, static_url_path="/chater/static")
app.secret_key = os.getenv("SECRET_KEY")
picFolder = "/app/static/pics/"
SESSION_LIFETIME = int(os.getenv("SESSION_LIFETIME"))
ALLOWED_EMAILS = os.getenv("ALLOWED_EMAILS", "").split(",")

google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
    scope=["profile", "email"],
    redirect_to="google_login",
)
app.register_blueprint(google_bp, url_prefix="/login")

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
    return chater_ui(session, target='chater')


@app.route("/chamini", methods=["GET", "POST"])
def chamini():
    return chater_ui(session, target='chamini')


@app.route("/gempt", methods=["GET", "POST"])
def gempt():
    return chater_ui(session, target='gempt')


@app.route("/chater_clear_responses", methods=["GET"])
def chater_clear_responses():
    return chater_clear(session=session)


@app.route("/chater_logout")
def chater_logout():
    return logout(session=session)


@app.route("/chater_wait")
def chater_wait():
    logging.warning("Waiting for next chater_login attempt")
    return render_template("wait.html")


@app.route("/gphoto", methods=["GET"])
def gphoto_ui():
    return gphoto(session, picFolder)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    logger = logging.getLogger("werkzeug")
    logger.setLevel(logging.INFO)
    app.run(host="0.0.0.0")
