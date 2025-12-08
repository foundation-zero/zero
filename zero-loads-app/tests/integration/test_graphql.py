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
            ActualType(id="headstay-load", value=1.0),
            ActualType(id="main-sheet-load", value=2.0),
        ]
    )
    return mock


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
                variables(variables: ["headstay-load", "main-sheet-load"]) {
                    actual {
                        value
                        id
                    }
                    reference(
                        sails: [full_main_sail, main_blade, full_mizzen_sail]
                        case: {seaState: wet, pcsMode: {fwd: propulsion, aft: propulsion}, awa: 1.5, aws: 1.5}
                    ) {
                        masts {
                            id
                            name
                        }
                        target {
                            unit
                            target
                        }
                        value {
                            name
                            id
                        }
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
                    "actual": {"value": 1.0, "id": "headstay-load"},
                    "reference": {
                        "masts": {"id": "main", "name": "Main mast"},
                        "target": {"unit": "tonne", "target": "2.0"},
                        "value": {"name": "Headstay load", "id": "headstay-load"},
                    },
                },
                {"actual": {"value": 2.0, "id": "main-sheet-load"}, "reference": None},
            ]
        }
    }
