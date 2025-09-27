import os

from common import configure_logging
from models_processor import ModelsProcessor


def main() -> None:
    configure_logging()
    port = int(os.getenv("PORT", "8000"))

    processor = ModelsProcessor()
    processor.start()

    try:
        processor.app.run(host="0.0.0.0", port=port, use_reloader=False)
    finally:
        processor.stop()


if __name__ == "__main__":
    main()
