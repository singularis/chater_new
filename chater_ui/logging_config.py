import logging
import os
import sys
from tempfile import gettempdir


def setup_logging(log_file):
    log_dir = gettempdir()
    log_path = os.path.join(log_dir, log_file)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(log_path)],
    )
