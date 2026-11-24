"""Shorter zmqtt log lines that name their broker.

zmqtt logs every failed reconnect with a full traceback, and its module loggers
can't tell two clients apart.

TODO(ZERO-2668, ZERO-2669): drop this once zmqtt does both itself.
Copied from zero-modbus-bridge.
"""

import logging
from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar

_broker_name: ContextVar[str | None] = ContextVar("broker_name", default=None)


@contextmanager
def log_prefix(broker_name: str) -> Generator[None]:
    """zmqtt lines logged in this block, or by tasks started in it, start with the name."""
    token = _broker_name.set(broker_name)
    try:
        yield
    finally:
        _broker_name.reset(token)


class _ZmqttFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        if record.exc_info and record.levelno < logging.ERROR:
            exc = record.exc_info[1]
            message = f"{message}: {type(exc).__name__}: {exc}"
            record.exc_info = None
        if name := _broker_name.get():
            message = f"{name}: {message}"
        record.msg, record.args = message, ()
        return True


for _logger_name in ("zmqtt.client", "zmqtt.protocol"):
    logging.getLogger(_logger_name).addFilter(_ZmqttFilter())
