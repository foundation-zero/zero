import logging
import sys


def setup_logging(log_level=logging.INFO):
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(name)-8s | %(levelname)-6s | %(message)s",
        stream=sys.stdout,
        force=True,
    )
