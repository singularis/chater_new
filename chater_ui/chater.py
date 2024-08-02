from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    logging,
)
import logging
import sys
from kafka_producer import produce_message
import uuid


log = logging.getLogger('main')


def chater(session):
    if "logged_in" in session:
        if request.method == "POST":
            question = request.form["question"]
            message = {
                'key': str(uuid.uuid4()),
                'value': question
            }
            produce_message(topic="dlp-source", message=message)
            if "responses" not in session:
                session["responses"] = []
            temp_responses = ["test"]
            while sys.getsizeof(temp_responses) > 2000:
                temp_responses.pop()
            session["responses"] = temp_responses[:2]
            return redirect(url_for("chater"))
        return render_template("chater.html", responses=session.get("responses", []))
    else:
        logging.warning("Unauthorized chater access attempt")
        flash("You need to log in to view this page")
        return redirect(url_for("chater_login"))
