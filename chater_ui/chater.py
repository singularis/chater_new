import json
import logging
import re
import uuid

from flask import flash, redirect, render_template, request, url_for

from common import sanitize_question
from kafka_consumer import consume_messages, create_consumer
from kafka_producer import create_producer, produce_message
from logging_config import setup_logging

setup_logging("app.log")
log = logging.getLogger("main")


TARGET_CONFIG = {
    "chater": {
        "target": "chater",
        "send_topic": "gpt-send",
        "receive_topic": ["gpt-response"],
    },
    "chamini": {
        "target": "chamini",
        "send_topic": "gemini-send",
        "receive_topic": ["gemini-response"],
    },
}


def get_target_config(target):
    return TARGET_CONFIG.get(target)


def chater(session, target):
    if "logged_in" not in session:
        log.warning("Unauthorized chater access attempt")
        flash("You need to log in to view this page")
        return redirect(url_for("chater_login"))

    if request.method == "POST":
        target_config = get_target_config(target)
        if not target_config:
            log.error(f"Invalid target: {target}")
            flash("Invalid target specified")
            return redirect(url_for("chater"))

        question = request.form["question"]
        question = sanitize_question(question=question)
        log.info(f"Asked question in UI: {question}")
        question_uuid = str(uuid.uuid4())
        message = {
            "key": question_uuid,
            "value": {
                "question": question,
                "send_topic": target_config["send_topic"],
                "context": session.get("context", None),
                "think": True,
            },
        }
        log.info(f"message {message}")
        producer = create_producer()
        produce_message(producer, topic="dlp-source", message=message)
        json_response = get_messages(
            question_uuid, topics=target_config["receive_topic"]
        )
        log.info(f"Message response {json_response}")
        if session.get("switch_state", "off") == "on":
            session["context"] = session["context"] + question + json_response
            log.info(f"Context crated {session['context'] }")
        else:
            session["context"] = None
        formatted_script = format_script(json_response)
        log.info(f"Formated data {formatted_script}")
        new_response = {
            "question": question,
            "response": formatted_script,
            "full": json_response,
        }

        session["responses"] = manage_session_responses(
            session.get("responses", []), new_response
        )
        return redirect(url_for(target_config["target"]))

    return render_template("chater.html", responses=session.get("responses", []))


def get_messages(message_uuid, topics):
    log.info(
        f"Starting message processing with topics: {topics}, looking for {message_uuid}"
    )
    consumer = create_consumer(topics)
    log.info(f"message_uuid {message_uuid}")

    for message in consume_messages(consumer):
        try:
            value = message.value().decode("utf-8")
            value_dict = json.loads(value)
            consumer.commit(message)
            return value_dict.get("value")
        except Exception as e:
            log.error(f"Failed to process message: {e}")
            return "Timeout"


def format_script(json_response):
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

    try:
        json_string = re.search(r"```json\n(.*?)\n```", json_response, re.DOTALL)
        if json_string:
            json_response = json_string.group(1)

        response_data = json.loads(json_response)
        script_content = next(
            (response_data[key] for key in possible_keys if key in response_data), None
        )
        if script_content is not None:
            return (
                "\n".join(script_content)
                if isinstance(script_content, list)
                else script_content
            )
        else:
            return json.dumps(response_data, indent=2)
    except (json.JSONDecodeError, TypeError) as e:
        return json_response


def manage_session_responses(existing_responses, new_response):
    existing_responses.insert(0, new_response)
    return existing_responses
