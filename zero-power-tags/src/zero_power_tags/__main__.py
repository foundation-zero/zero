import contextlib
import signal

from pydantic_settings import CliApp

from zero_power_tags.cli import ZeroPowerTags

if __name__ == "__main__":
    # As PID 1, SIGTERM is ignored unless handled.
    signal.signal(signal.SIGTERM, lambda *_: signal.raise_signal(signal.SIGINT))
    with contextlib.suppress(KeyboardInterrupt):
        CliApp.run(ZeroPowerTags)
