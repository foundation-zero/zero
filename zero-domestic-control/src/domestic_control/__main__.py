import contextlib
import signal

from pydantic_settings import CliApp

from .cli import DomesticControl


def run():
    # As PID 1, SIGTERM is ignored unless handled.
    signal.signal(signal.SIGTERM, lambda *_: signal.raise_signal(signal.SIGINT))
    with contextlib.suppress(KeyboardInterrupt):
        CliApp.run(DomesticControl)


if __name__ == "__main__":
    run()
