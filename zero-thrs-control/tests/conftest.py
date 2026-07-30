import asyncio
import os
import socket
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, Mock

import pytest

from thrs.classes.database import PostgresDatabase
from thrs.orchestration.config import Config


@pytest.fixture(scope="session")
def settings():
    os.environ["MQTT_HOST"] = "localhost"
    os.environ["MQTT_DEVICES_TOPIC_PREFIX"] = "test_devices_topic"
    os.environ["MQTT_CONTROLLER_TOPIC_PREFIX"] = "test_controller_topic"
    os.environ["MQTT_SIMULATOR_TOPIC_PREFIX"] = "test_simulation_topic"
    os.environ["MQTT_CONTROL_TOPIC_SUFFIX"] = "control"
    os.environ["MQTT_CONTROLLER_TOPIC_SUFFIX"] = "set"
    os.environ["MQTT_SIMULATOR_TOPIC_SUFFIX"] = "set"
    return Config()  # type: ignore


@pytest.fixture(scope="session")
def app(settings):
    from thrs.graphql.strawberry import create_app  # noqa: PLC0415

    return create_app(settings)


@pytest.fixture(scope="session", autouse=True)
def ensure_default_event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        yield
    finally:
        loop.close()
        asyncio.set_event_loop(None)


@pytest.fixture(autouse=True)
def ensure_event_loop_per_test():
    """Ensure sync tests also have a current default loop on Python 3.12+."""
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    yield


@pytest.fixture
def mock_session() -> Mock:
    session = Mock()
    session.add = Mock()
    session.commit = AsyncMock()
    return session


@pytest.fixture
def postgres_db(mock_session: Mock) -> Mock:
    @asynccontextmanager
    async def session_factory() -> AsyncIterator[Mock]:
        yield mock_session

    postgres_db = Mock(spec=PostgresDatabase)
    postgres_db.session_factory = session_factory
    return postgres_db


def _mqtt_is_available(host: str, port: int, timeout_s: float = 0.2) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout_s):
            return True
    except OSError:
        return False


def pytest_runtest_setup(item):
    if "mqtt" not in item.keywords:
        return

    host = os.environ.get("MQTT_HOST", "localhost")
    port = int(os.environ.get("MQTT_PORT", "1883"))
    if not _mqtt_is_available(host, port):
        pytest.skip(f"MQTT broker not available at {host}:{port}")
