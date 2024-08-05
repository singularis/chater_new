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
from kafka_consumer import create_consumer, consume_messages
import uuid
import json

log = logging.getLogger("main")


def targets(target):
    if target == "chater":
        return {"target": "chater", "send_topic": "gpt-send", "receive_topic": ["gpt-response"]}
    elif target == "chamini":
        return {"target": "chamini", "send_topic": "gemini-send", "receive_topic": ["gemini-response"]}
    elif target == "gempt":
        return


def chater(session, target):
    if "logged_in" in session:
        if request.method == "POST":
            question_uuid = None
            target = targets(target)
            question = request.form["question"]
            logging.info(f"Asked question in UI: {question}")
            question_uuid = str(uuid.uuid4())
            message = {"key": question_uuid, "value": {"question": question, "send_topic": target["send_topic"]}}
            logging.info(f"message {message}")
            produce_message(topic="dlp-source", message=message)
            json_response = get_messages(question_uuid, topics=target["receive_topic"])
            logging.info(f"Gemini message {json_response}")
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
                "question": question,
                "response": formatted_script,
                "full": json_response,
            }
            if "responses" not in session:
                session["responses"] = []
            temp_responses = [new_response] + session["responses"]
            while sys.getsizeof(temp_responses) > 2000:
                temp_responses.pop()
            session["responses"] = temp_responses[:2]
            return redirect(url_for(target["target"]))
        return render_template("chater.html", responses=session.get("responses", []))
    else:
        logging.warning("Unauthorized chater access attempt")
        flash("You need to log in to view this page")
        return redirect(url_for("chater_login"))


def get_messages(message_uuid, topics):
    log.info(f"Starting message processing with topics: {topics}, looking for {message_uuid}")
    consumer = create_consumer(topics)
    while True:
        for message in consume_messages(consumer):
            try:
                value = message.value().decode("utf-8")
                value_dict = json.loads(value)
                actual_uuid = value_dict["key"]
                consumer.commit(message)
                if actual_uuid == message_uuid:
                    log.info(f"Found send message for requested uuid {message_uuid}")
                    actual_value = value_dict["value"]
                    log.info(f"actual_value {actual_value}")
                    return actual_value
            except Exception as e:
                log.error(f"Failed to process message: {e}")
                return f"Timeout"
