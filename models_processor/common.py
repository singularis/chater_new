import json
import logging
import os
from typing import Any, Dict, Optional

LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s %(message)s"
DEFAULT_LOG_LEVEL = "WARNING"


DEFAULT_LEVEL_MAPPING = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "WARN": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "NOTSET": logging.NOTSET,
}


def _resolve_log_level(level_name: str) -> int:
    if isinstance(level_name, int):
        return level_name

    if isinstance(level_name, str):
        value = level_name.strip()
        if value.isdigit():
            return int(value)

        normalized = value.upper()
        if normalized in DEFAULT_LEVEL_MAPPING:
            return DEFAULT_LEVEL_MAPPING[normalized]

    logging.warning("Invalid log level '%s'; defaulting to WARNING", level_name)
    return logging.WARNING


def configure_logging(default_level: str = DEFAULT_LOG_LEVEL) -> None:
    log_level_name = os.getenv("LOG_LEVEL", default_level)
    logging.basicConfig(level=_resolve_log_level(log_level_name), format=LOG_FORMAT)


def _decode_bytes(raw_value: Any) -> Optional[str]:
    if isinstance(raw_value, (bytes, bytearray)):
        try:
            return raw_value.decode("utf-8")
        except UnicodeDecodeError as exc:
            logging.error("Failed to decode Kafka message bytes: %s", exc)
            return None
    if isinstance(raw_value, str):
        return raw_value
    logging.error("Unexpected Kafka message value type: %s", type(raw_value))
    return None


def load_kafka_payload(message_value: Any) -> Optional[Dict[str, Any]]:
    payload_str = _decode_bytes(message_value)
    if payload_str is None:
        return None

    try:
        return json.loads(payload_str)
    except json.JSONDecodeError as exc:
        logging.error("Failed to parse Kafka message JSON: %s", exc)
        return None
