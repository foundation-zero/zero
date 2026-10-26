from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError
from pydantic_settings import CliApp

from zero_alert_forwarder.alert import AlertPriority, AlertUpdate
from zero_alert_forwarder.cli import ZeroAlertForwarder

REQUIRED = [
    "--mysql-hosts",
    '["localhost", "mirror"]',
    "--mysql-user",
    "chameleon",
    "--mysql-password",
    "secret",
    "--ntfy-topic",
    "crew",
]


@pytest.fixture(autouse=True)
def isolated_env(monkeypatch: pytest.MonkeyPatch):
    for name in (
        "MYSQL_HOSTS",
        "MYSQL_USER",
        "MYSQL_PASSWORD",
        "NTFY_TOPIC",
        "UPDATES",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.chdir("/")


def run(*args: str) -> ZeroAlertForwarder:
    with patch.object(ZeroAlertForwarder, "cli_cmd") as cli_cmd:
        settings = CliApp.run(
            ZeroAlertForwarder, [*REQUIRED, *args], cli_exit_on_error=False
        )
        cli_cmd.assert_called_once()
        return settings


def test_defaults():
    settings = run()

    assert settings.mysql_hosts == ["localhost", "mirror"]
    assert settings.mysql_database == "alerts"
    assert settings.ntfy_url == "https://ntfy.sh"
    assert settings.poll_interval_seconds == 10
    assert settings.min_priority is AlertPriority.WARNING
    assert settings.updates == {AlertUpdate.ACTIVATED}
    assert settings.mysql_password.get_secret_value() == "secret"


def test_overrides():
    settings = run(
        "--min-priority", "Caution", "--ntfy-url", "https://ntfy.vessel", "--dry-run"
    )

    assert settings.min_priority is AlertPriority.CAUTION
    assert settings.ntfy_url == "https://ntfy.vessel"
    assert settings.dry_run


def test_readiness_path():
    assert run().readiness_path is None
    assert run("--readiness-path", "/tmp/ready").readiness_path == Path("/tmp/ready")


@pytest.mark.parametrize("seconds", ["0", "-1"])
def test_rejects_non_positive_poll_timeout(seconds: str):
    with pytest.raises(ValidationError):
        run("--poll-timeout-seconds", seconds)


def test_liveness_path():
    assert run().liveness_path is None
    assert run("--liveness-path", "/tmp/liveness").liveness_path == Path(
        "/tmp/liveness"
    )


def test_updates_from_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("UPDATES", '["Activated", "Idle"]')

    assert run().updates == {AlertUpdate.ACTIVATED, AlertUpdate.IDLE}


@pytest.mark.parametrize("seconds", ["0.5", "61"])
def test_rejects_poll_interval_outside_range(seconds: str):
    with pytest.raises(ValidationError):
        run("--poll-interval-seconds", seconds)


def test_requires_topic():
    with pytest.raises(ValidationError):
        with patch.object(ZeroAlertForwarder, "cli_cmd"):
            CliApp.run(ZeroAlertForwarder, REQUIRED[:-2], cli_exit_on_error=False)
