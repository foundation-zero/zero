import signal

from pydantic_settings import CliApp

from zero_alert_forwarder.cli import ZeroAlertForwarder

if __name__ == "__main__":
    # As PID 1, SIGTERM is ignored unless handled.
    signal.signal(signal.SIGTERM, lambda *_: signal.raise_signal(signal.SIGINT))
    try:
        CliApp.run(ZeroAlertForwarder)
    except KeyboardInterrupt:
        pass
