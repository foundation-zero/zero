import logging
from typing import Protocol

import httpx
from pydantic import SecretStr

from zero_alert_forwarder.alert import Alert, AlertPriority

logger = logging.getLogger(__name__)


class Notifier(Protocol):
    async def notify(self, alert: Alert) -> None: ...


class NtfyNotifier:
    def __init__(
        self,
        client: httpx.AsyncClient,
        topic: str,
        token: SecretStr | None = None,
    ):
        self._client = client
        self._topic = topic
        self._headers = (
            {"Authorization": f"Bearer {token.get_secret_value()}"} if token else {}
        )

    async def notify(self, alert: Alert) -> None:
        # The JSON API, as headers cannot carry the non-ASCII text the AMCS emits.
        response = await self._client.post(
            "/",
            json={
                "topic": self._topic,
                "sequence_id": _sequence_id(alert),
                "title": _title(alert),
                "message": alert.description or alert.tag or "No description",
                "priority": alert.priority.severity,
                "tags": _tags(alert.priority),
                "timestamp": int(alert.event_time.timestamp()),
            },
            headers=self._headers,
        )
        response.raise_for_status()


class LogNotifier:
    async def notify(self, alert: Alert) -> None:
        logger.info(f"Would notify: {_title(alert)}: {alert.description}")


def _sequence_id(alert: Alert) -> str:
    """Identical on every pod and mirror, so ntfy updates instead of repeats a notification."""
    return f"{alert.event_time:%Y%m%d}-{alert.id}"


def _title(alert: Alert) -> str:
    return " | ".join(
        part for part in (alert.priority.value, alert.system, alert.location) if part
    )


def _tags(priority: AlertPriority) -> list[str]:
    match priority:
        case AlertPriority.GEA | AlertPriority.EMERGENCY:
            return ["rotating_light"]
        case AlertPriority.ALARM | AlertPriority.WARNING:
            return ["warning"]
        case _:
            return []
