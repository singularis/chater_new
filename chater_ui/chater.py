from flask import render_template, redirect, url_for, flash, request
import logging
import uuid
import json
import sys
from kafka_producer import produce_message, create_producer
from kafka_consumer import create_consumer, consume_messages
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
        log.info(f"Asked question in UI: {question}")
        question_uuid = str(uuid.uuid4())
        message = {
            "key": question_uuid,
            "value": {
                "question": question,
                "send_topic": target_config["send_topic"],
            },
        }
        log.info(f"message {message}")
        producer = create_producer()
        produce_message(producer, topic="dlp-source", message=message)
        json_response = get_messages(question_uuid, topics=target_config["receive_topic"])
        log.info(f"Message {json_response}")

        formatted_script = format_script(json_response)
        new_response = {
            "question": question,
            "response": formatted_script,
            "full": json_response,
        }

        session["responses"] = manage_session_responses(session.get("responses", []), new_response)
        return redirect(url_for(target_config["target"]))

    return render_template("chater.html", responses=session.get("responses", []))


def get_messages(message_uuid, topics):
    log.info(f"Starting message processing with topics: {topics}, looking for {message_uuid}")
    consumer = create_consumer(topics)
    log.info(f"message_uuid {message_uuid}")

    for message in consume_messages(consumer):
        try:
            value = message.value().decode("utf-8")
            value_dict = json.loads(value)
            if value_dict.get("key") == message_uuid:
                log.info(f"Found message for requested uuid {message_uuid}")
                return value_dict.get("value")
            consumer.commit(message)
        except Exception as e:
            log.error(f"Failed to process message: {e}")
            return "Timeout"


def format_script(json_response):
    possible_keys = [
        "script", "code", "bash_script", "python_code", "javascript_code",
        "java_code", "csharp_code", "php_code", "ruby_code", "swift_code",
        "perl_code", "sql_code", "html_code", "css_code", "python_script",
        "javascript_script", "java_script", "csharp_script", "php_script",
        "ruby_script", "swift_script", "perl_script", "sql_script", "html_script",
        "css_script", "Python_Script",
    ]

    try:
        response_data = json.loads(json_response)
        script_content = next((response_data[key] for key in possible_keys if key in response_data), response_data)
        return "\n".join(script_content) if isinstance(script_content, list) else script_content
    except json.JSONDecodeError:
        return json_response


def manage_session_responses(existing_responses, new_response):
    temp_responses = [new_response] + existing_responses
    while sys.getsizeof(temp_responses) > 2000:
        temp_responses.pop()
    return temp_responses[:2]
