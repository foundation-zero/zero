import json
from datetime import UTC, datetime

import httpx
import pytest
from pydantic import SecretStr

from zero_alert_forwarder.alert import AlertPriority
from zero_alert_forwarder.ntfy import NtfyNotifier

from .conftest import make_alert


def notifier(
    handler, token: SecretStr | None = None
) -> tuple[NtfyNotifier, list[httpx.Request]]:
    requests: list[httpx.Request] = []

    def record(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return handler(request)

    client = httpx.AsyncClient(
        base_url="https://ntfy.example", transport=httpx.MockTransport(record)
    )
    return NtfyNotifier(client, "crew", token), requests


async def test_publishes_alert_as_json():
    ntfy, requests = notifier(lambda _: httpx.Response(200))

    await ntfy.notify(
        make_alert(
            priority=AlertPriority.EMERGENCY,
            system="450000 DYNAMIC CONV",
            location="TS",
            description="Breaker tripped — check",
        )
    )

    [request] = requests
    assert (request.method, str(request.url)) == ("POST", "https://ntfy.example/")
    assert "Authorization" not in request.headers
    assert json.loads(request.content) == {
        "topic": "crew",
        "sequence_id": "20261022-1",
        "title": "Emergency | 450000 DYNAMIC CONV | TS",
        "message": "Breaker tripped — check",
        "priority": 5,
        "tags": ["rotating_light"],
        "timestamp": 1792688400,
    }


async def test_same_alert_gets_the_same_sequence_id():
    ntfy, requests = notifier(lambda _: httpx.Response(200))

    await ntfy.notify(make_alert(5, description="first publish"))
    await ntfy.notify(make_alert(5, description="second publish"))
    await ntfy.notify(make_alert(6))

    sequence_ids = [json.loads(request.content)["sequence_id"] for request in requests]
    assert sequence_ids == ["20261022-5", "20261022-5", "20261022-6"]


async def test_sequence_id_differs_per_day():
    ntfy, requests = notifier(lambda _: httpx.Response(200))

    await ntfy.notify(make_alert(5))
    await ntfy.notify(
        make_alert(5, event_time=datetime(2026, 10, 23, 0, 1, tzinfo=UTC))
    )

    sequence_ids = [json.loads(request.content)["sequence_id"] for request in requests]
    assert sequence_ids == ["20261022-5", "20261023-5"]


async def test_authenticates_with_token():
    ntfy, requests = notifier(lambda _: httpx.Response(200), SecretStr("tk_secret"))

    await ntfy.notify(make_alert())

    assert requests[0].headers["Authorization"] == "Bearer tk_secret"


async def test_message_falls_back_when_alert_has_no_description():
    ntfy, requests = notifier(lambda _: httpx.Response(200))

    await ntfy.notify(make_alert(tag="KEB7.BREAKER"))
    await ntfy.notify(make_alert())

    messages = [json.loads(request.content)["message"] for request in requests]
    assert messages == ["KEB7.BREAKER", "No description"]


async def test_failed_publish_raises():
    ntfy, _ = notifier(lambda _: httpx.Response(429))

    with pytest.raises(httpx.HTTPStatusError):
        await ntfy.notify(make_alert())
