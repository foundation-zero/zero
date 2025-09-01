import logging
import sys


def setup_logging(log_level=logging.INFO):
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        stream=sys.stdout,
    )
