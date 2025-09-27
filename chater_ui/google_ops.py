import logging
import os

from flask import flash, redirect, url_for
from flask_dance.contrib.google import google, make_google_blueprint

logger = logging.getLogger(__name__)


def create_google_blueprint():
    google_bp = make_google_blueprint(
        client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
        scope=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
        ],
        redirect_to="google_login",
    )
    return google_bp


def g_login(session, ALLOWED_EMAILS):
    logger.info("Google login initiated")
    if not google.authorized:
        logger.debug("User not authorized with Google; redirecting to OAuth flow")
        return redirect(url_for("google.login"))
    try:
        resp = google.get("/oauth2/v1/userinfo")
        resp.raise_for_status()
    except Exception as e:
        logger.error("Google login error: %s", e)
        flash("An error occurred during Google login", "error")
        return redirect(url_for("google.login"))
    user_info = resp.json()
    user_email = user_info.get("email")
    if user_email in ALLOWED_EMAILS:
        session["logged_in"] = True
        session["google_id"] = user_info.get("id")
        session["user_email"] = user_email
        session.permanent = True
        return redirect(url_for("chamini"))
    else:
        logger.warning("Unauthorized Google email attempted login: %s", user_email)
        session["logged_in"] = False
        session.permanent = False
        flash("Email not authorized", "error")
        return redirect(url_for("chater_logout"))
