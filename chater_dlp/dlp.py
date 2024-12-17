import json
import logging
import os
import re

from dlp_types import INFO_TYPES
from google.cloud import dlp_v2
from google.cloud.dlp_v2.types import (
    DeidentifyConfig,
    InfoTypeTransformations,
    PrimitiveTransformation,
    ReplaceValueConfig,
)
from kafka_consumer import consume_messages
from kafka_producer import produce_message


def inspect_and_redact(text: str) -> str:
    dlp = dlp_v2.DlpServiceClient()
    project_id = os.getenv("GCP_PROJECT_ID")

    item = {"value": text}

    info_types = INFO_TYPES
    inspect_config = {"info_types": info_types}

    replace_config = ReplaceValueConfig(new_value={"string_value": "[REDACTED]"})
    primitive_transformation = PrimitiveTransformation(replace_config=replace_config)

    info_type_transformations = InfoTypeTransformations(
        transformations=[
            {
                "info_types": info_types,
                "primitive_transformation": primitive_transformation,
            }
        ]
    )
    deidentify_config = DeidentifyConfig(
        info_type_transformations=info_type_transformations
    )

    response = dlp.deidentify_content(
        request={
            "parent": f"projects/{project_id}",
            "inspect_config": inspect_config,
            "item": item,
            "deidentify_config": deidentify_config,
        }
    )
    logging.info(f"Response from DLP {response.item.value}")
    return response.item.value


def process_messages():
    topics = ["dlp-source"]
    logging.info(f"Starting message processing with topics: {topics}")
    while True:
        for message, consumer in consume_messages(topics):
            try:
                key = message.key().decode("utf-8") if message.key() else None
                value = message.value().decode("utf-8")

                value_dict = json.loads(value)
                actual_value = value_dict["value"]
                question = actual_value["question"]
                send_topic = actual_value["send_topic"]

                redacted_value = inspect_and_redact(question)
                redacted_data = {
                    "question": redacted_value,
                    "context": actual_value["context"],
                }
                redacted_message = {"key": key, "value": redacted_data}

                produce_message(send_topic, redacted_message)
                logging.info(
                    f"Processed and redacted message: {redacted_message}, send to topic {send_topic}"
                )

                consumer.commit(message)
            except Exception as e:
                logging.error(f"Failed to process message: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting DLP processing script")
    process_messages()
