from pydantic_settings import CliApp

from zero_alert_forwarder.cli import ZeroAlertForwarder

if __name__ == "__main__":
    try:
        CliApp.run(ZeroAlertForwarder)
    except KeyboardInterrupt:
        pass
