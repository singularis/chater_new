from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    logging,
)
import logging
import json
import sys

log = logging.getLogger('main')


def chater(session):
    if "logged_in" in session:
        if request.method == "POST":
            question = request.form["question"]
            chater_response = chater_request(question)
            chater_response = {"response_content":"test", "safe_question":"test"}
            json_response = chater_response["response_content"]
            try:
                response_data = json.loads(json_response)
                possible_keys = [
                    "script",
                    "code",
                    "bash_script",
                    "python_code",
                    "javascript_code",
                    "java_code",
                    "csharp_code",
                    "php_code",
                    "ruby_code",
                    "swift_code",
                    "perl_code",
                    "sql_code",
                    "html_code",
                    "css_code",
                    "python_script",
                    "javascript_script",
                    "java_script",
                    "csharp_script",
                    "php_script",
                    "ruby_script",
                    "swift_script",
                    "perl_script",
                    "sql_script",
                    "html_script",
                    "css_script",
                    "Python_Script",
                ]
                script_content = next(
                    (
                        response_data[key]
                        for key in possible_keys
                        if key in response_data
                    ),
                    response_data,
                )
                formatted_script = (
                    "\n".join(script_content)
                    if isinstance(script_content, list)
                    else script_content
                )
            except json.JSONDecodeError:
                formatted_script = json_response
            new_response = {
                "question": chater_response["safe_question"],
                "response": formatted_script,
                "full": json_response,
            }
            if "responses" not in session:
                session["responses"] = []
            temp_responses = [new_response] + session["responses"]
            while sys.getsizeof(temp_responses) > 2000:
                temp_responses.pop()
            session["responses"] = temp_responses[:2]
            return redirect(url_for("chater"))
        return render_template("chater.html", responses=session.get("responses", []))
    else:
        logging.warning("Unauthorized chater access attempt")
        flash("You need to log in to view this page")
        return redirect(url_for("chater_login"))
