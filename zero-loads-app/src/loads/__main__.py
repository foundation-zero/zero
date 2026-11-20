import contextlib
import signal

from pydantic_settings import CliApp

from .cli import ZeroLoads


def run_app():
    # As PID 1, SIGTERM is ignored unless handled.
    signal.signal(signal.SIGTERM, lambda *_: signal.raise_signal(signal.SIGINT))
    with contextlib.suppress(KeyboardInterrupt):
        CliApp.run(ZeroLoads)


if __name__ == "__main__":
    run_app()
