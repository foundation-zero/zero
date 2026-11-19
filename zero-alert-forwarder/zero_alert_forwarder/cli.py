import asyncio
import json
import logging
from datetime import timedelta
from pathlib import Path
from typing import Annotated

import aiomqtt
import httpx
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, CliApp, CliSubCommand, SettingsConfigDict

from zero_alert_forwarder.alarm_list import AlarmList
from zero_alert_forwarder.alert import AlertPriority, AlertUpdate
from zero_alert_forwarder.asyncapi import build_asyncapi
from zero_alert_forwarder.forwarder import Forwarder
from zero_alert_forwarder.liveness import Liveness
from zero_alert_forwarder.mqtt import ALARM_LIST_TOPIC, AlarmListPublisher
from zero_alert_forwarder.mysql import MysqlDayTables
from zero_alert_forwarder.ntfy import LogNotifier, Notifier, NtfyNotifier
from zero_alert_forwarder.readiness import Readiness
from zero_alert_forwarder.source import PollingAlertSource

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s"
)


SETTINGS_CONFIG = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    extra="allow",
    env_nested_delimiter="__",
    cli_implicit_flags=True,
    cli_ignore_unknown_args=True,
)


class RunCmd(BaseSettings):
    model_config = SETTINGS_CONFIG

    mysql_hosts: Annotated[list[str], Field(min_length=1)]
    mysql_port: int = 3306
    mysql_user: str
    mysql_password: SecretStr
    mysql_database: str = "alerts"

    ntfy_url: str = "https://ntfy.sh"
    ntfy_topic: str
    ntfy_token: SecretStr | None = None

    poll_interval_seconds: Annotated[float, Field(ge=1, le=60)] = 10
    min_priority: AlertPriority = AlertPriority.WARNING
    updates: set[AlertUpdate] = {AlertUpdate.ACTIVATED}
    attempts: Annotated[int, Field(ge=1)] = 3
    reminder_delays_seconds: list[Annotated[float, Field(gt=0)]] = [20, 10, 5, 3, 1]
    dry_run: bool = False
    poll_timeout_seconds: Annotated[float, Field(gt=0)] = 10
    history_timeout_seconds: Annotated[float, Field(gt=0)] = 60
    liveness_path: Path | None = None
    readiness_path: Path | None = None

    mqtt_host: str | None = None
    mqtt_port: int = 1883
    mqtt_username: str | None = None
    mqtt_password: SecretStr | None = None
    alarm_list_min_priority: AlertPriority = AlertPriority.WARNING
    alarm_list_window_minutes: Annotated[float, Field(gt=0)] = 60
    # Readers drop the list after 30s without an update.
    alarm_list_interval_seconds: Annotated[float, Field(ge=1, le=10)] = 5

    async def cli_cmd(self) -> None:
        interval = timedelta(seconds=self.poll_interval_seconds)
        logger.info(
            f"Starting alert forwarder: polling {', '.join(self.mysql_hosts)}"
            f" (port {self.mysql_port}, database {self.mysql_database})"
            f" each every {interval.total_seconds():g}s, forwarding {self.min_priority} and up"
            f" ({', '.join(sorted(self.updates))}) to {self.ntfy_url}"
            f"{' (dry run)' if self.dry_run else ''}"
        )
        tables = [
            MysqlDayTables(
                host,
                self.mysql_port,
                self.mysql_user,
                self.mysql_password,
                self.mysql_database,
            )
            for host in self.mysql_hosts
        ]
        window = timedelta(minutes=self.alarm_list_window_minutes)
        alarms = (
            AlarmList(self.alarm_list_min_priority, window) if self.mqtt_host else None
        )
        async with (
            httpx.AsyncClient(base_url=self.ntfy_url, timeout=10) as client,
            asyncio.TaskGroup() as tasks,
        ):
            notifier: Notifier = (
                LogNotifier()
                if self.dry_run
                else NtfyNotifier(client, self.ntfy_topic, self.ntfy_token)
            )
            forwarder = Forwarder(
                PollingAlertSource(
                    tables,
                    interval,
                    liveness=Liveness(self.liveness_path),
                    readiness=Readiness(self.readiness_path),
                    poll_timeout=timedelta(seconds=self.poll_timeout_seconds),
                    history=alarms,
                    history_window=window,
                    history_timeout=timedelta(seconds=self.history_timeout_seconds),
                ),
                notifier,
                self.min_priority,
                self.updates,
                self.attempts,
                interval,
                [timedelta(seconds=delay) for delay in self.reminder_delays_seconds],
                alarms,
            )
            tasks.create_task(forwarder.run())
            if alarms:
                tasks.create_task(self._publisher(alarms).run())

    def _publisher(self, alarms: AlarmList) -> AlarmListPublisher:
        logger.info(
            f"Publishing alarms of {self.alarm_list_min_priority} and up to"
            f" {self.mqtt_host}:{self.mqtt_port}/{ALARM_LIST_TOPIC}"
        )
        return AlarmListPublisher(
            alarms,
            lambda: aiomqtt.Client(
                self.mqtt_host or "",
                self.mqtt_port,
                username=self.mqtt_username,
                password=self.mqtt_password.get_secret_value()
                if self.mqtt_password
                else None,
            ),
            timedelta(seconds=self.alarm_list_interval_seconds),
        )


class PrintAsyncApiCmd(BaseModel):
    """Prints the AsyncAPI spec of the alarm list, for zero-mqtt-graphql."""

    def cli_cmd(self) -> None:
        print(json.dumps(build_asyncapi(), indent=2))


class ZeroAlertForwarder(BaseSettings, cli_kebab_case=True):
    model_config = SETTINGS_CONFIG

    run: CliSubCommand[RunCmd]
    print_asyncapi: CliSubCommand[PrintAsyncApiCmd]

    def cli_cmd(self) -> None:
        if self.run or self.print_asyncapi:
            CliApp.run_subcommand(self)
        else:
            # The container starts without a subcommand, with its settings in the environment.
            CliApp.run(RunCmd, cli_args=[])
