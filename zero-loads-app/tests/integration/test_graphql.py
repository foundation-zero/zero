from unittest.mock import Mock

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from loads.api import app
from loads.api.api import get_messaging
from loads.api.types import ActualType


def override_messaging():
    mock = Mock()

    mock.get_values_for = Mock(
        return_value=[
            ActualType(id="main-sheet-load", value=42.0),
        ]
    )
    return mock


@pytest.fixture
async def async_client():
    async with LifespanManager(app) as manager:
        async with AsyncClient(
            transport=ASGITransport(app=manager.app), base_url="http://test"
        ) as client:
            yield client


@pytest.mark.asyncio
async def test_graphql_reference(async_client: AsyncClient):
    app.dependency_overrides[get_messaging] = override_messaging

    response = await async_client.post(
        "/graphql",
        json={
            "query": """
            query {
                variables(variables: ["main-sheet-load"]) {
                    id
                    reference(case: {awa: 27, aws: 16, sailset: [full_main, full_mizzen, blade]}) {
                    reference {
                        alarmLow
                        alarmHigh
                        target
                        warningHigh
                        warningLow
                    }
                    variable {
                        id
                        name
                        unit
                    }
                    }
                    actual {
                    id
                    value
                    }
                }
            }
            """
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "variables": [
                {
                    "id": "main-sheet-load",
                    "reference": {
                        "reference": {
                            "alarmLow": None,
                            "alarmHigh": 15.0,
                            "target": None,
                            "warningHigh": None,
                            "warningLow": None,
                        },
                        "variable": {
                            "id": "main-sheet-load",
                            "name": "Main Sheet Load",
                            "unit": "tonne",
                        },
                    },
                    "actual": {"id": "main-sheet-load", "value": 42.0},
                }
            ]
        }
    }
