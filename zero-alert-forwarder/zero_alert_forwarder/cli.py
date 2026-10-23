import logging
from datetime import timedelta
from pathlib import Path
from typing import Annotated

import httpx
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from zero_alert_forwarder.alert import AlertPriority, AlertUpdate
from zero_alert_forwarder.forwarder import Forwarder
from zero_alert_forwarder.liveness import Liveness
from zero_alert_forwarder.mysql import MysqlDayTables
from zero_alert_forwarder.ntfy import LogNotifier, Notifier, NtfyNotifier
from zero_alert_forwarder.readiness import Readiness
from zero_alert_forwarder.source import PollingAlertSource

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s"
)


class ZeroAlertForwarder(BaseSettings, cli_kebab_case=True):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
        env_nested_delimiter="__",
        cli_implicit_flags=True,
        cli_ignore_unknown_args=True,
    )

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
    dry_run: bool = False
    poll_timeout_seconds: Annotated[float, Field(gt=0)] = 10
    liveness_path: Path | None = None
    readiness_path: Path | None = None

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
        async with httpx.AsyncClient(base_url=self.ntfy_url, timeout=10) as client:
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
                ),
                notifier,
                self.min_priority,
                self.updates,
                self.attempts,
                interval,
            )
            await forwarder.run()
