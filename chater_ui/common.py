from datetime import datetime, timedelta
from flask import (
    redirect,
    url_for,
    flash, request,
)
import logging

log = logging.getLogger("main")


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
        flash("Responses cleared successfully")
        referrer = request.referrer
        if referrer:
            return redirect(referrer)
        else:
            return redirect(url_for('chater'))
    else:
        logging.warning("Unauthorized clear attempt")
        flash("You need to log in to perform this action")
        return redirect(url_for("chater_login"))

