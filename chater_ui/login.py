from datetime import datetime, timedelta
import logging
from flask import (
    redirect,
    url_for,
    flash,
    render_template,
)
import os
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, DataRequired
from werkzeug.security import check_password_hash
from flask_dance.contrib.google import make_google_blueprint, google


USERNAME = os.getenv("USERNAME")
PASSWORD_HASH = os.getenv("PASSWORD_HASH")
LAST_FAILED_ATTEMPT_TIME = None


class ChaterLoginForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired()], render_kw={"autocomplete": "username"}
    )
    password = PasswordField("Password", validators=[InputRequired()])


log = logging.getLogger("main")


def login(session, target):
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


def logout(session):
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
