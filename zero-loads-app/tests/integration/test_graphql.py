from unittest.mock import Mock

import pytest
from httpx import AsyncClient

from loads.api.dependencies import get_messaging
from loads.registry.registry import VARIABLES
from loads.sensors.at import ApparentWindSpeed
from loads.sensors.fiber_optic import SideStayMeasurements
from loads.sensors.sail_system import MainCheckstay, PrimaryWinchPs


def override_messaging():
    mock = Mock()

    mock.get_variable_value = Mock(return_value=42.0)

    return mock


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
                        reference(case: {awaRange: upwind, awsRange: aws_20_25, sailset: ["full-main", "full-mizzen", "blade"]}) {
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
                            "alarmLow": None,
                            "warningLow": None,
                            "target": 17.3,
                            "warningHigh": 23.76,
                            "alarmHigh": 26.4,
                        },
                        "actual": {
                            "id": "main-runner-ps-load",
                            "value": 42.0,
                        },
                        "variable": {
                            "id": "main-runner-ps-load",
                            "name": "runner ps",
                            "unit": "tonne",
                            "scaleMin": 0.0,
                            "scaleMax": 29.0,
                            "scaleMinLabel": None,
                            "scaleMaxLabel": None,
                        },
                    },
                ]
            }
        }


@pytest.mark.asyncio
async def test_graphql_set_reference_values(async_client: AsyncClient):
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
async def test_graphql_all_variables(async_client: AsyncClient):
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
async def test_graphql_variable_duplicates(async_client: AsyncClient):
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
async def test_graphql_reference_duplicates(async_client: AsyncClient):
    response = await async_client.post(
        "/graphql",
        json={
            "query": """
            query {
                variables(variables: ["main-runner-ps-load"]) {
                    id
                    a: reference(case: {awaRange: upwind, awsRange: aws_20_25, sailset: ["full-main", "full-mizzen", "blade"]}) {
                        alarmLow
                        alarmHigh
                        target
                        warningHigh
                        warningLow
                    }
                    b: reference(case: {awaRange: upwind, awsRange: aws_20_25, sailset: ["full-main", "full-mizzen", "blade"]}) {
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
                        "alarmLow": None,
                        "warningLow": None,
                        "target": 17.3,
                        "warningHigh": 23.76,
                        "alarmHigh": 26.4,
                    },
                    "b": {
                        "alarmLow": None,
                        "warningLow": None,
                        "target": 17.3,
                        "warningHigh": 23.76,
                        "alarmHigh": 26.4,
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
async def test_alarms(async_client: AsyncClient, mqtt_client_send):
    await mqtt_client_send.publish(
        MainCheckstay.TOPIC,
        """{
            "relative_position_dummy": 500,
            "i_ActualLoadPs": 420,
            "i_ActualLoadSb": 400,
            "ow_ActLoad_10kg": 500,
            "ow_RelfLoad_10kg": 400,
            "ox_LoadAlarm": true
        }""",
    )
    response = await async_client.post(
        "/graphql",
        json={
            "query": """
            query {
                alarms(alarms: ["main-checkstay-alarm"]) {
                    id
                    name
                    thresholdValue
                    actualValue
                    active
                    actual {
                        id
                        variable {
                            unit
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
            "alarms": [
                {
                    "id": "main-checkstay-alarm",
                    "name": "Main Checkstay Alarm",
                    "active": True,
                    "thresholdValue": 4.0,
                    "actualValue": 5.0,
                    "actual": {
                        "id": "main-checkstay-deflector-load",
                        "variable": {
                            "unit": "tonne",
                        },
                    },
                },
            ]
        }
    }


@pytest.mark.asyncio
async def test_active_alarms(async_client: AsyncClient, mqtt_client_send):
    await mqtt_client_send.publish(
        MainCheckstay.TOPIC,
        """{
            "relative_position_dummy": 500,
            "i_ActualLoadPs": 420,
            "i_ActualLoadSb": 400,
            "ow_ActLoad_10kg": 500,
            "ow_RelfLoad_10kg": 400,
            "ox_LoadAlarm": true
        }""",
    )
    response = await async_client.post(
        "/graphql",
        json={
            "query": """
            query {
                alarms(active: true) {
                    id
                    thresholdValue
                    actualValue
                    active
                }
            }
            """
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "alarms": [
                {
                    "id": "main-checkstay-alarm",
                    "active": True,
                    "thresholdValue": 4.0,
                    "actualValue": 5.0,
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
async def test_fiber_optics_actual(async_client: AsyncClient, mqtt_client_send):
    await mqtt_client_send.publish(
        SideStayMeasurements.TOPIC,
        """{
            "v1": 20,
            "d1": 1,
            "d2": 2,
            "d3": 3,
            "d4": 4,
            "d5": 5
        }""",
    )
    response = await async_client.post(
        "/graphql",
        json={
            "query": """
            query {
                variables(variables: ["side-stay-measurements-v1"]) {
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
                    "id": "side-stay-measurements-v1",
                    "actual": {
                        "id": "side-stay-measurements-v1",
                        "value": 20,
                    },
                },
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
