import os
from openai import OpenAI
import logging
import json
from kafka_consumer import consume_messages
from kafka_producer import produce_message

MODEL = os.getenv("MODEL")
client = OpenAI()


def gpt_request(question, context=None) -> dict[str, str]:
    logging.info(f"GPT Question: {question}")

    # Base messages with the system message and user question
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant designed to output JSON. "
                       "Oriented on software development, python, java, AWS, SRE",
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


def process_messages():
    topics = ["gpt-send"]
    logging.info(f"Starting message processing with topics: {topics}")
    while True:
        for message, consumer in consume_messages(topics):
            try:
                key = message.key().decode("utf-8") if message.key() else None
                value = message.value().decode("utf-8")

                value_dict = json.loads(value)
                actual_value = value_dict["value"]
                context = actual_value["context"]
                question = actual_value["question"]
                response_value = gpt_request(question, context)
                kafka_message = {"key": key, "value": response_value}

                produce_message("gpt-response", kafka_message)
                logging.info(
                    f"Processed and redacted message send to kafka: {kafka_message}"
                )

                consumer.commit(message)
            except Exception as e:
                logging.error(f"Failed to process message: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting GPT processing script")
    process_messages()
