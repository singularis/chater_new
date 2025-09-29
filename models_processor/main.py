import os

from logging_config import setup_logging

from models_processor import ModelsProcessor


def main() -> None:
    setup_logging("models_processor.log")
    port = int(os.getenv("PORT", "8000"))

    processor = ModelsProcessor()
    processor.start()

    try:
        processor.app.run(host="0.0.0.0", port=port, use_reloader=False)
    finally:
        processor.stop()


if __name__ == "__main__":
    main()
