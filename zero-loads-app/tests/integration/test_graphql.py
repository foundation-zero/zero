from unittest.mock import Mock

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from loads.api import app
from loads.api.api import get_messaging
from loads.api.types import ActualType


async def override_messaging():
    mock = Mock()
    mock.get_value_for = Mock(return_value=[ActualType(id="test-load", value=42.0)])
    yield mock


@pytest.fixture
async def async_client():
    async with LifespanManager(app) as manager:
        async with AsyncClient(transport=ASGITransport(app=manager.app), base_url="http://test") as client:
            yield client


@pytest.mark.asyncio
async def test_graphql_reference(async_client: AsyncClient):
    app.dependency_overrides[get_messaging] = override_messaging

    response = await async_client.post(
        "/graphql",
        json={
            "query": """
            query {
                reference(
                    variables: "headstay-load"
                    case: {pcsMode: {aft: propulsion, fwd: propulsion}, aws: 25, awa: 0, seaState: wet}
                    sails: [full_mizzen_sail, full_main_sail, main_blade, mizzen_jib]
                )
                {
                    ranges {
                        errorTooHigh
                        errorTooLow
                        warningTooHigh
                        warningTooLow
                    }
                    target {
                        target
                        unit
                    }
                    value {
                        id
                        name
                    }
                    masts {
                        id
                        name
                    }
                }
            }
            """
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "reference": [
                {
                    "ranges": {
                        "errorTooHigh": None,
                        "errorTooLow": None,
                        "warningTooHigh": None,
                        "warningTooLow": None,
                    },
                    "target": {"target": "5.0", "unit": "tonne"},
                    "value": {"id": "headstay-load", "name": "Headstay load"},
                    "masts": {"id": "main", "name": "Main mast"},
                },
                {
                    "ranges": {
                        "errorTooHigh": None,
                        "errorTooLow": None,
                        "warningTooHigh": None,
                        "warningTooLow": None,
                    },
                    "target": {"target": "2.5", "unit": "tonne"},
                    "value": {"id": "headstay-load", "name": "Headstay load"},
                    "masts": {"id": "mizzen", "name": "Mizzen mast"},
                },
            ]
        }
    }


@pytest.mark.asyncio
async def test_graphql_actuals(async_client: AsyncClient):
    app.dependency_overrides[get_messaging] = override_messaging

    response = await async_client.post(
        "/graphql",
        json={
            "query": """
            query {
                actual(variables: "test-load") {
                    id
                    value
                }
            }
            """
        },
    )

    assert response.status_code == 200
    assert response.json() == {"data": {"actual": [{"id": "test-load", "value": 42.0}]}}
