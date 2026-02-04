from unittest.mock import Mock

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from loads.api import app
from loads.api.api import get_messaging
from loads.api.loads import loads_variables
from loads.api.types import ActualType
from loads.sensors.at import ApparentWindSpeed


def override_messaging():
    mock = Mock()

    mock.get_values_for = Mock(
        return_value=[
            ActualType(id="main-checkstay-ps-load", value=42.0),
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
async def test_graphql_reference(async_client: AsyncClient, override_dependency):
    with override_dependency(get_messaging, override_messaging):
        response = await async_client.post(
            "/graphql",
            json={
                "query": """
                query {
                    variables(variables: ["main-checkstay-ps-load"]) {
                        id
                        reference(case: {awaRange: upwind, awsRange: aws_15_20, sailset: [full_main, full_mizzen, blade]}) {
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
                            minimum
                            maximum
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
                        "id": "main-checkstay-ps-load",
                        "reference": {
                            "alarmLow": 5.0,
                            "warningLow": 6.0,
                            "target": 10.0,
                            "warningHigh": 14.0,
                            "alarmHigh": 15.0,
                        },
                        "actual": {
                            "id": "main-checkstay-ps-load",
                            "value": 42.0,
                        },
                        "variable": {
                            "id": "main-checkstay-ps-load",
                            "name": "Main Checkstay Ps Load",
                            "unit": "tonne",
                            "minimum": 0.0,
                            "maximum": None,
                        },
                    },
                ]
            }
        }


@pytest.mark.asyncio
async def test_graphql_all_variables(async_client: AsyncClient, override_dependency):
    with override_dependency(get_messaging, override_messaging):
        response = await async_client.post(
            "/graphql",
            json={
                "query": """
                query {
                    variables {
                        id
                        variable {
                            id
                            name
                            unit
                            minimum
                            maximum
                        }
                    }
                }
                """
            },
        )

        assert response.status_code == 200
        assert len(response.json()["data"]["variables"]) == len(loads_variables.keys())


@pytest.mark.asyncio
async def test_at_sensors(async_client: AsyncClient, mqtt_client_send):
    variable_name = "aws"
    raw_value = "16.7"
    await mqtt_client_send.publish(ApparentWindSpeed.TOPIC, raw_value)
    response = await async_client.post(
        "/graphql",
        json={
            "query": """
            query {
                variables(variables: ["%s"]) {
                    id
                    actual {
                        id
                        value
                    }
                }
            }
            """
            % variable_name
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "variables": [
                {
                    "id": variable_name,
                    "actual": {"id": variable_name, "value": float(raw_value)},
                }
            ]
        }
    }
