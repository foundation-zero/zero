import logging
import os
import sys


def setup_logging():
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        stream=sys.stdout,
    )
