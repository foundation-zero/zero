from contextlib import asynccontextmanager
from unittest.mock import Mock

from httpx import AsyncClient

from loads.api.db import SessionManager
from loads.api.dependencies import get_sessionmanager


async def test_live(async_client: AsyncClient):
    response = await async_client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


async def test_ready(async_client: AsyncClient):
    response = await async_client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def override_sessionmanager():
    mock = Mock(spec=SessionManager)

    @asynccontextmanager
    async def fail():
        raise Exception("Database connection failed")
        yield

    mock.session.side_effect = fail

    return mock


async def test_ready_db_failure(async_client: AsyncClient, override_dependency):
    with override_dependency(get_sessionmanager, override_sessionmanager):
        response = await async_client.get("/health/ready")
        assert response.status_code == 500
        json_response = response.json()
        assert json_response["status"] == "not ready"
        assert "Database connection failed" in json_response["error"]
