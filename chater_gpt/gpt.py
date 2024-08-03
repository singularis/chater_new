import os
from openai import OpenAI
import logging
import json
from kafka_consumer import consume_messages
from kafka_producer import produce_message

MODEL = os.getenv("MODEL")
client = OpenAI()


def gpt_request(question) -> dict[str, str]:
    logging.info(f"GPT Question {question}")
    response = client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant designed to output JSON.",
            },
            {"role": "user", "content": question},
        ],
    )
    response_content = response.choices[0].message.content
    logging.info(f"GPT Answer {response_content}")
    return response_content


def process_messages():
    topics = ["dlp-response"]
    logging.info(f"Starting message processing with topics: {topics}")
    while True:
        for message, consumer in consume_messages(topics):
            try:
                key = message.key().decode("utf-8") if message.key() else None
                value = message.value().decode("utf-8")

                value_dict = json.loads(value)
                actual_value = value_dict["value"]

                response_value = gpt_request(actual_value)
                kafka_message = {"key": key, "value": response_value}

                produce_message("gpt-response", kafka_message)
                logging.info(f"Processed and redacted message send to kafka: {kafka_message}")

                consumer.commit(message)
            except Exception as e:
                logging.error(f"Failed to process message: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting GPT processing script")
    process_messages()
