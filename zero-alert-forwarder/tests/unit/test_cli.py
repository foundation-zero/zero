import json
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError
from pydantic_settings import CliApp

from zero_alert_forwarder.alert import AlertPriority, AlertUpdate
from zero_alert_forwarder.cli import RunCmd, ZeroAlertForwarder
from zero_alert_forwarder.mqtt import ALARM_LIST_TOPIC

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


def run(*args: str) -> RunCmd:
    with patch.object(RunCmd, "cli_cmd") as cli_cmd:
        forwarder = CliApp.run(
            ZeroAlertForwarder, ["run", *REQUIRED, *args], cli_exit_on_error=False
        )
        cli_cmd.assert_called_once()
    assert forwarder.run
    return forwarder.run


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
        with patch.object(RunCmd, "cli_cmd"):
            CliApp.run(
                ZeroAlertForwarder, ["run", *REQUIRED[:-2]], cli_exit_on_error=False
            )


def test_alarm_list_defaults():
    settings = run()

    assert settings.mqtt_host is None
    assert settings.mqtt_port == 1883
    assert settings.alarm_list_min_priority is AlertPriority.WARNING
    assert settings.alarm_list_window_minutes == 60
    assert settings.alarm_list_interval_seconds == 5


def test_alarm_list_overrides():
    settings = run(
        "--mqtt-host",
        "vernemq",
        "--mqtt-password",
        "secret",
        "--alarm-list-min-priority",
        "Caution",
        "--alarm-list-window-minutes",
        "30",
    )

    assert settings.mqtt_host == "vernemq"
    assert settings.mqtt_password
    assert settings.mqtt_password.get_secret_value() == "secret"
    assert settings.alarm_list_min_priority is AlertPriority.CAUTION
    assert settings.alarm_list_window_minutes == 30


@pytest.mark.parametrize("seconds", ["0.5", "11"])
def test_rejects_alarm_list_interval_outside_range(seconds: str):
    with pytest.raises(ValidationError):
        run("--alarm-list-interval-seconds", seconds)


def test_runs_from_the_environment_without_subcommand(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("MYSQL_HOSTS", '["localhost"]')
    monkeypatch.setenv("MYSQL_USER", "chameleon")
    monkeypatch.setenv("MYSQL_PASSWORD", "secret")
    monkeypatch.setenv("NTFY_TOPIC", "crew")

    with patch.object(RunCmd, "cli_cmd", autospec=True) as cli_cmd:
        CliApp.run(ZeroAlertForwarder, [], cli_exit_on_error=False)

    [settings] = cli_cmd.call_args.args
    assert settings.mysql_hosts == ["localhost"]
    assert settings.ntfy_topic == "crew"


def test_print_asyncapi_needs_no_settings(capsys: pytest.CaptureFixture[str]):
    with patch.object(RunCmd, "cli_cmd") as cli_cmd:
        CliApp.run(ZeroAlertForwarder, ["print-asyncapi"], cli_exit_on_error=False)

    cli_cmd.assert_not_called()
    spec = json.loads(capsys.readouterr().out)
    assert spec["channels"]["alarmList"]["address"] == ALARM_LIST_TOPIC
