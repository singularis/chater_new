import logging
import os
import sys
from tempfile import gettempdir
from typing import Dict, Optional

DEFAULT_LOG_LEVEL = "INFO"


def _parse_log_level(log_level: Optional[str]) -> int:
    """Convert string-based log level to logging numeric level with fallback."""

    if not log_level:
        return logging.INFO

    if isinstance(log_level, str):
        normalized = log_level.strip().upper()
        if normalized.isdigit():
            return int(normalized)
        mapping_fn = getattr(logging, "getLevelNamesMapping", None)
        if callable(mapping_fn):
            level_mapping = {
                str(name).upper(): int(value)
                for name, value in mapping_fn().items()
                if isinstance(value, int)
            }
        else:
            level_mapping = getattr(logging, "_nameToLevel", {})
        numeric_level = level_mapping.get(normalized)
        if isinstance(numeric_level, int):
            return numeric_level

    return logging.INFO


def get_log_level_from_env() -> int:
    """Read the LOG_LEVEL env var and return the numeric logging level."""

    env_value = os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL)
    parsed_level = _parse_log_level(env_value)
    if parsed_level == logging.INFO and env_value.upper() != "INFO":
        logging.warning("Unrecognised LOG_LEVEL '%s'; defaulting to INFO", env_value)
    return parsed_level


def setup_logging(log_file: str) -> None:
    """Configure root logger with stdout and file handlers respecting LOG_LEVEL."""

    log_dir = gettempdir()
    log_path = os.path.join(log_dir, log_file)

    root_logger = logging.getLogger()
    root_logger.setLevel(get_log_level_from_env())

    formatter = logging.Formatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Prevent duplicate handlers when re-initialising (e.g. in tests)
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)

    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)
