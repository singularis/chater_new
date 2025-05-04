import json
import logging
import os

from kafka_consumer import consume_messages
from kafka_producer import produce_message
from openai import OpenAI

MODEL = os.getenv("MODEL")
VISION_MODEL = os.getenv("VISION_MODEL")
client = OpenAI()


def gpt_request(question, context=None, content=None) -> dict[str, str]:
    logging.info(f"GPT Question: {question}")

    if MODEL == "o1-mini":
        messages = [{"role": "user", "content": question}]
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
        )
    else:
        system_message = (
            content
            if content
            else (
                "You are a helpful assistant designed to output JSON. "
                "Oriented on software development, python, java, AWS, SRE."
            )
        )
        messages = [
            {
                "role": "system",
                "content": system_message,
            },
            {"role": "user", "content": question},
        ]
        if context:
            context_string = " ".join(
                [str(item) for item in context if item is not None]
            )
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
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": str(prompt),
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{photo_base64}"
                            },
                        },
                    ],
                }
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
                value_dict = json.loads(value)
                actual_value = value_dict["value"]

                if topic == "gpt-send":
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
                    prompt = actual_value.get("prompt")
                    photo_base64 = actual_value.get("photo")
                    user_email = actual_value.get("user_email")
                    if prompt and photo_base64:
                        photo_analysis_result = analyze_photo(prompt, photo_base64)
                        kafka_message = {
                            "key": key,
                            "value": {
                                "analysis": photo_analysis_result,
                                "user_email": user_email,
                            },
                        }
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
