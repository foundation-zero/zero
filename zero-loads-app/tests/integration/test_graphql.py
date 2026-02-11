from unittest.mock import Mock

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from loads.api import app
from loads.api.api import get_messaging
from loads.api.types import ActualType
from loads.registry.registry import VARIABLES
from loads.sensors.at import ApparentWindSpeed
from loads.sensors.sail_system import PrimaryWinchPs


def override_messaging():
    mock = Mock()

    mock.get_values_for = Mock(
        return_value=[
            ActualType(id="main-runner-ps-load", value=42.0),
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
async def test_graphql(async_client: AsyncClient, override_dependency):
    with override_dependency(get_messaging, override_messaging):
        response = await async_client.post(
            "/graphql",
            json={
                "query": """
                query {
                    variables(variables: ["main-runner-ps-load"]) {
                        id
                        reference(case: {awaRange: upwind, awsRange: aws_15_20, sailset: ["full-main", "full-mizzen", "blade"]}) {
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
                            scaleMin
                            scaleMax
                            scaleMinLabel
                            scaleMaxLabel
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
                        "id": "main-runner-ps-load",
                        "reference": {
                            "alarmLow": 6.0,
                            "warningLow": 9.0,
                            "target": 12.0,
                            "warningHigh": 15.0,
                            "alarmHigh": 18.0,
                        },
                        "actual": {
                            "id": "main-runner-ps-load",
                            "value": 42.0,
                        },
                        "variable": {
                            "id": "main-runner-ps-load",
                            "name": "runner ps load",
                            "unit": "tonne",
                            "scaleMin": 0.0,
                            "scaleMax": 20.0,
                            "scaleMinLabel": None,
                            "scaleMaxLabel": None,
                        },
                    },
                ]
            }
        }


@pytest.mark.asyncio
async def test_graphql_set_reference_values(
    async_client: AsyncClient, override_dependency
):
    insert = await async_client.post(
        "/graphql",
        json={
            "query": """
            mutation {
                setReferenceValues(
                    awaRanges: [upwind, reaching]
                    awsRanges: [aws_0_10, aws_10_15]
                    referenceValue: {id: "blade-adjuster-load", target: 100}
                    sailSet: ["full-main", "full-mizzen"]
                )
            }
            """
        },
    )

    assert insert.status_code == 200

    response = await async_client.post(
        "/graphql",
        json={
            "query": """
            query {
                variables(variables: ["blade-adjuster-load"]) {
                    id
                    reaching: reference(case: {awaRange: reaching, awsRange: aws_0_10, sailset: ["full-main", "full-mizzen"]}) {
                        target
                    }
                    upwind: reference(case: {awaRange: upwind, awsRange: aws_0_10, sailset: ["full-main", "full-mizzen"]}) {
                        target
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
                    "id": "blade-adjuster-load",
                    "reaching": {"target": 100.0},
                    "upwind": {"target": 100.0},
                }
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
                            scaleMin
                            scaleMax
                            scaleMinLabel
                            scaleMaxLabel
                        }
                    }
                }
                """
            },
        )

        assert response.status_code == 200
        assert len(response.json()["data"]["variables"]) == len(VARIABLES.keys())


@pytest.mark.asyncio
async def test_graphql_variable_duplicates(
    async_client: AsyncClient, override_dependency
):
    with override_dependency(get_messaging, override_messaging):
        response = await async_client.post(
            "/graphql",
            json={
                "query": """
                query {
                    a: variables {
                        id
                        variable {
                            id
                            name
                            unit
                            scaleMin
                            scaleMax
                            scaleMinLabel
                            scaleMaxLabel
                        }
                    }
                    b: variables {
                        id
                        variable {
                            id
                            name
                            unit
                            scaleMin
                            scaleMax
                            scaleMinLabel
                            scaleMaxLabel
                        }
                    }
                }
                """
            },
        )

        assert response.status_code == 200
        assert len(response.json()["data"]["a"]) == len(VARIABLES.keys())
        assert len(response.json()["data"]["b"]) == len(VARIABLES.keys())


@pytest.mark.asyncio
async def test_graphql_reference_duplicates(
    async_client: AsyncClient, override_dependency
):
    with override_dependency(get_messaging, override_messaging):
        response = await async_client.post(
            "/graphql",
            json={
                "query": """
                query {
                    variables(variables: ["main-runner-ps-load"]) {
                        id
                        a: reference(case: {awaRange: upwind, awsRange: aws_15_20, sailset: ["full-main", "full-mizzen", "blade"]}) {
                            alarmLow
                            alarmHigh
                            target
                            warningHigh
                            warningLow
                        }
                        b: reference(case: {awaRange: upwind, awsRange: aws_15_20, sailset: ["full-main", "full-mizzen", "blade"]}) {
                            alarmLow
                            alarmHigh
                            target
                            warningHigh
                            warningLow
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
                        "id": "main-runner-ps-load",
                        "a": {
                            "alarmLow": 6.0,
                            "warningLow": 9.0,
                            "target": 12.0,
                            "warningHigh": 15.0,
                            "alarmHigh": 18.0,
                        },
                        "b": {
                            "alarmLow": 6.0,
                            "warningLow": 9.0,
                            "target": 12.0,
                            "warningHigh": 15.0,
                            "alarmHigh": 18.0,
                        },
                    },
                ]
            }
        }


@pytest.mark.asyncio
async def test_sail_system_actual(async_client: AsyncClient, mqtt_client_send):
    await mqtt_client_send.publish(
        PrimaryWinchPs.TOPIC,
        """{
            "ow_ActLoad_10kg": 420,
            "ow_RelfLoad_10kg": 500,
            "ox_LoadAlarm": false
        }""",
    )
    response = await async_client.post(
        "/graphql",
        json={
            "query": """
            query {
                variables(variables: ["primary-winch-ps-load"]) {
                    id
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
                    "id": "primary-winch-ps-load",
                    "actual": {
                        "id": "primary-winch-ps-load",
                        "value": 4.2,
                    },
                },
            ]
        }
    }


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


@pytest.mark.asyncio
async def test_sails(async_client: AsyncClient):
    response = await async_client.post(
        "/graphql",
        json={
            "query": """
            query {
                sails {
                    id
                    abbreviation
                    positionId
                    name
                    variantName
                }
            }
            """
        },
    )

    assert response.status_code == 200
    sails = response.json()["data"]["sails"]
    assert len(sails) > 0


@pytest.mark.asyncio
async def test_sails_single(async_client: AsyncClient):
    response = await async_client.post(
        "/graphql",
        json={
            "query": """
            query {
                sails(sails: ["full-main"]) {
                    id
                    abbreviation
                    variantName
                    name
                    positionId
                }
            }
            """
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "sails": [
                {
                    "id": "full-main",
                    "abbreviation": "FM",
                    "positionId": "main",
                    "name": "Full Main",
                    "variantName": "Full",
                }
            ]
        }
    }
