import logging
from flask import (
    redirect,
    url_for,
    flash,
)
from flask_dance.contrib.google import google


log = logging.getLogger("main")


def g_login(session, ALLOWED_EMAILS):
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
