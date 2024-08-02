from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    flash,
    session,
    logging,
)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, DataRequired
from werkzeug.security import check_password_hash
from flask_dance.contrib.google import make_google_blueprint, google
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import logging
from datetime import datetime, timedelta
from gphoto import gphoto
from chater import chater as chater_ui

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = Flask(__name__, static_url_path="/chater/static")
app.secret_key = os.getenv("SECRET_KEY")
LAST_FAILED_ATTEMPT_TIME = None
picFolder = "/app/static/pics/"

USERNAME = os.getenv("USERNAME")
PASSWORD_HASH = os.getenv("PASSWORD_HASH")
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


class ChaterLoginForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired()], render_kw={"autocomplete": "username"}
    )
    password = PasswordField("Password", validators=[InputRequired()])


@app.before_request
def before_request():
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


@app.route("/chater_login", methods=["GET", "POST"])
def chater_login():
    global LAST_FAILED_ATTEMPT_TIME
    if LAST_FAILED_ATTEMPT_TIME and (
        datetime.now() - LAST_FAILED_ATTEMPT_TIME
    ) < timedelta(seconds=30):
        logging.warning("Too many failed attempts")
        flash("Too many failed attempts. Please try again later.")
        return redirect(url_for("chater_wait"))
    else:
        form = ChaterLoginForm()
        if form.validate_on_submit():
            if form.username.data == USERNAME and check_password_hash(
                PASSWORD_HASH, form.password.data
            ):
                logging.info("Successful chater_login by user: %s", form.username.data)
                session.permanent = True
                session["logged_in"] = True
                return redirect(url_for("chater"))
            else:
                LAST_FAILED_ATTEMPT_TIME = datetime.now()
                logging.warning(
                    "Failed chater_login attempt for user: %s", form.username.data
                )
            flash("Wrong password", "error")
        return render_template("login.html", form=form)


@app.route("/google_login")
def google_login():
    logging.info("Google login")
    if not google.authorized:
        logging.info("User not authorized with Google")
        return redirect(url_for("google.login"))
    try:
        resp = google.get("/oauth2/v1/userinfo")
        resp.raise_for_status()
    except Exception as e:
        logging.error(f"Google login error: {e}")
        flash("An error occurred during Google login", "error")
        return redirect(url_for("google.login"))
    user_info = resp.json()
    user_email = user_info["email"]
    if user_email in ALLOWED_EMAILS:
        session["logged_in"] = True
        session["google_id"] = user_info["id"]
        session["user_email"] = user_email
        session.permanent = True
        return redirect(url_for("chater"))
    else:
        logging.error(
            f"Email {user_email} with {user_info} is not authorized for chater"
        )
        flash("Email not authorized", "error")
        return redirect(url_for("chater_login"))


@app.route("/chater", methods=["GET", "POST"])
def chater():
    return chater_ui(session)


@app.route("/chater_clear_responses", methods=["GET"])
def chater_clear_responses():
    if "logged_in" in session:
        session["responses"] = []
        flash("Responses cleared successfully")
        return redirect(url_for("chater"))
    else:
        logging.warning("Unauthorized clear attempt")
        flash("You need to log in to perform this action")
        return redirect(url_for("chater_login"))


@app.route("/chater_logout")
def chater_logout():
    logging.info("Logged out")
    if google.authorized:
        try:
            response = google.post(
                "https://accounts.google.com/o/oauth2/revoke",
                params={"token": google.token["access_token"]},
                headers={"content-type": "application/x-www-form-urlencoded"},
            )
            assert response.ok, "Failed to revoke token"
            session.pop("google_id", None)
            session.pop("user_email", None)
        except Exception as e:
            logging.error(f"Failed to revoke Google token: {e}")
    session.pop("logged_in", None)
    return redirect(url_for("chater_login"))


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
