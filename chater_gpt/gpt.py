import os
import base64
from openai import OpenAI
import logging
import json
from kafka_consumer import consume_messages
from kafka_producer import produce_message

MODEL = os.getenv("MODEL")
client = OpenAI()


def gpt_request(question, context=None, content=None) -> dict[str, str]:
    logging.info(f"GPT Question: {question}")

    system_message = content if content else (
        "You are a helpful assistant designed to output JSON. "
        "Oriented on software development, python, java, AWS, SRE."
    )

    # Base messages with the system message and user question
    messages = [
        {
            "role": "system",
            "content": system_message,
        },
        {"role": "user", "content": question},
    ]
    if context:
        context_string = " ".join([str(item) for item in context if item is not None])
        messages.append({"role": "assistant", "content": context_string})

    response = client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        messages=messages,
    )

    response_content = response.choices[0].message.content
    logging.info(f"GPT Answer: {response_content}")

    return response_content


def analyze_photo(prompt, photo_base64):
    try:
        logging.info("Analyzing photo with prompt via ChatGPT.")
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI that analyzes photos and provides insights based on prompts."
                },
                {"role": "user", "content": prompt},
                {"role": "user", "content": f"Photo Base64: {photo_base64}"}
            ],
        )

        response_content = response.choices[0].message.content
        logging.info(f"Photo analysis result: {response_content}")

        return response_content
    except Exception as e:
        logging.error(f"Failed to analyze photo: {e}")
        return None


def process_messages():
    topics = ["gpt-send", "eater-send-photo"]
    logging.info(f"Starting message processing with topics: {topics}")
    while True:
        for message, consumer in consume_messages(topics):
            try:
                topic = message.topic()
                key = message.key().decode("utf-8") if message.key() else None
                value = message.value().decode("utf-8")

                if topic == "gpt-send":
                    value_dict = json.loads(value)
                    actual_value = value_dict["value"]
                    context = actual_value.get("context")
                    question = actual_value.get("question")
                    response_value = gpt_request(question, context)
                    kafka_message = {"key": key, "value": response_value}

                    produce_message("gpt-response", kafka_message)
                    logging.info(
                        f"Processed GPT message and sent to Kafka: {kafka_message}"
                    )

                elif topic == "eater-send-photo":
                    logging.info("Received message on 'eater-send-photo'.")
                    value_dict = json.loads(value)
                    prompt = value_dict.get("prompt")
                    photo_base64 = value_dict.get("photo")
                    if prompt and photo_base64:
                        photo_analysis_result = analyze_photo(prompt, photo_base64)
                        kafka_message = {"key": key, "value": photo_analysis_result}
                        produce_message("photo-analysis-response", kafka_message)
                        logging.info(
                            f"Photo analyzed and result sent to Kafka: {kafka_message}"
                        )
                    else:
                        logging.warning(
                            "Message on 'eater-send-photo' missing 'prompt' or 'photo'."
                        )

                consumer.commit(message)
            except Exception as e:
                logging.error(f"Failed to process message: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting GPT processing script")
    process_messages()
