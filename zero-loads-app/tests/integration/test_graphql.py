import asyncio
import json
from pathlib import Path
from unittest.mock import Mock

import pytest
from httpx import AsyncClient

from loads.api.dependencies import get_messaging
from loads.registry.registry import VARIABLES
from loads.sensors.at import ApparentWindSpeed
from loads.sensors.fiber_optic import FiberOptic
from loads.sensors.sail_system import MainCheckstay, PrimaryWinchPs


def override_messaging():
    mock = Mock()

    mock.get_variable_value = Mock(return_value=42.0)

    return mock


@pytest.fixture(autouse=True)
async def seed_graphql_scenarios(scenario_factory):
    await scenario_factory.seed_graphql_reference_defaults()
    await scenario_factory.seed_mutation_target_cases()


@pytest.mark.asyncio
async def test_graphql(async_client: AsyncClient, override_dependency):
    with override_dependency(get_messaging, override_messaging):
        response = await async_client.post(
            "/graphql",
            json={
                "query": """
                query {
                    variables(variables: ["main-sheet-load"]) {
                        id
                        reference(case: {awaRange: upwind, awsRange: aws_20_25, tack: starboard, sailset: ["full-main", "full-mizzen", "blade"]}) {
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
                        "id": "main-sheet-load",
                        "reference": {
                            "alarmLow": None,
                            "warningLow": None,
                            "target": 9.6,
                            "warningHigh": 13.5,
                            "alarmHigh": 15.0,
                        },
                        "actual": {
                            "id": "main-sheet-load",
                            "value": 42.0,
                        },
                        "variable": {
                            "id": "main-sheet-load",
                            "name": "Sheet",
                            "unit": "tonne",
                            "scaleMin": None,
                            "scaleMax": None,
                            "scaleMinLabel": None,
                            "scaleMaxLabel": None,
                        },
                    },
                ]
            }
        }


@pytest.mark.asyncio
async def test_graphql_symmetry(async_client: AsyncClient, override_dependency):
    with override_dependency(get_messaging, override_messaging):
        response = await async_client.post(
            "/graphql",
            json={
                "query": """
                query {
                    runner_sb: variables(variables: ["main-runner-sb-load"]) {
                        id
                        starboard_wind: reference(case: {awaRange: upwind, awsRange: aws_20_25, tack: starboard, sailset: ["full-main", "full-mizzen", "blade"]}) {
                            alarmLow
                            alarmHigh
                            target
                            warningHigh
                            warningLow
                        }
                        port_wind: reference(case: {awaRange: upwind, awsRange: aws_20_25, tack: port, sailset: ["full-main", "full-mizzen", "blade"]}) {
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
                    runner_ps: variables(variables: ["main-runner-ps-load"]) {
                        id
                        starboard_wind: reference(case: {awaRange: upwind, awsRange: aws_20_25, tack: starboard, sailset: ["full-main", "full-mizzen", "blade"]}) {
                            alarmLow
                            alarmHigh
                            target
                            warningHigh
                            warningLow
                        }
                        port_wind: reference(case: {awaRange: upwind, awsRange: aws_20_25, tack: port, sailset: ["full-main", "full-mizzen", "blade"]}) {
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
                "runner_sb": [
                    {
                        "id": "main-runner-sb-load",
                        "port_wind": None,
                        "starboard_wind": {
                            "alarmLow": None,
                            "warningLow": None,
                            "target": 17.3,
                            "warningHigh": 23.76,
                            "alarmHigh": 26.4,
                        },
                        "actual": {
                            "id": "main-runner-sb-load",
                            "value": 42.0,
                        },
                        "variable": {
                            "id": "main-runner-sb-load",
                            "name": "Runner SB",
                            "unit": "tonne",
                            "scaleMin": None,
                            "scaleMax": None,
                            "scaleMinLabel": None,
                            "scaleMaxLabel": None,
                        },
                    },
                ],
                "runner_ps": [
                    {
                        "id": "main-runner-ps-load",
                        "port_wind": {
                            "alarmLow": None,
                            "warningLow": None,
                            "target": 17.3,
                            "warningHigh": 23.76,
                            "alarmHigh": 26.4,
                        },
                        "starboard_wind": None,
                        "actual": {
                            "id": "main-runner-ps-load",
                            "value": 42.0,
                        },
                        "variable": {
                            "id": "main-runner-ps-load",
                            "name": "Runner PT",
                            "unit": "tonne",
                            "scaleMin": None,
                            "scaleMax": None,
                            "scaleMinLabel": None,
                            "scaleMaxLabel": None,
                        },
                    },
                ],
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
                    reaching: reference(case: {awaRange: reaching, awsRange: aws_0_10, tack: starboard, sailset: ["full-main", "full-mizzen"]}) {
                        target
                    }
                    upwind: reference(case: {awaRange: upwind, awsRange: aws_0_10, tack: starboard, sailset: ["full-main", "full-mizzen"]}) {
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
                variables(variables: ["main-sheet-load"]) {
                    id
                    a: reference(case: {awaRange: upwind, awsRange: aws_20_25, tack: starboard, sailset: ["full-main", "full-mizzen", "blade"]}) {
                        alarmLow
                        alarmHigh
                        target
                        warningHigh
                        warningLow
                    }
                    b: reference(case: {awaRange: upwind, awsRange: aws_20_25, tack: starboard, sailset: ["full-main", "full-mizzen", "blade"]}) {
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
                    "id": "main-sheet-load",
                    "a": {
                        "alarmLow": None,
                        "warningLow": None,
                        "target": 9.6,
                        "warningHigh": 13.5,
                        "alarmHigh": 15.0,
                    },
                    "b": {
                        "alarmLow": None,
                        "warningLow": None,
                        "target": 9.6,
                        "warningHigh": 13.5,
                        "alarmHigh": 15.0,
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
            "st_Load/i_Load": 420,
            "st_Load/x_Failure": false,
            "st_Load/x_MaxLimitReached": false,
            "st_Load/i_MaxLoadSetting": 500
        }""",
    )
    await asyncio.sleep(0.1)
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
            "st_position/i_Position_permille": 500,
            "st_position/x_MaxLimitReached": false,
            "st_position/x_MinLimitReached": false,
            "st_Load/i_Load": 500,
            "st_Load/x_Failure": false,
            "st_Load/x_MaxLimitReached": true,
            "st_Load/i_MaxLoadSetting": 400,
            "st_LoadPs/i_Load": 420,
            "st_LoadPs/i_MaxLoadSetting": 450,
            "st_LoadPs/x_MaxLimitReached": false,
            "st_LoadSb/i_Load": 500,
            "st_LoadSb/x_Failure": false,
            "st_LoadSb/i_MaxLoadSetting": 400,
            "st_LoadSb/x_MaxLimitReached": true
        }""",
    )
    await asyncio.sleep(0.1)
    response = await async_client.post(
        "/graphql",
        json={
            "query": """
            query {
                alarms(alarms: ["main-checkstay-deflector-load-alarm"]) {
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
                    "id": "main-checkstay-deflector-load-alarm",
                    "name": "Main Deflector Load Alarm",
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
            "st_position/i_Position_permille": 500,
            "st_position/x_MaxLimitReached": false,
            "st_position/x_MinLimitReached": false,
            "st_Load/i_Load": 500,
            "st_Load/x_Failure": false,
            "st_Load/x_MaxLimitReached": true,
            "st_Load/i_MaxLoadSetting": 400,
            "st_LoadPs/i_Load": 420,
            "st_LoadPs/i_MaxLoadSetting": 450,
            "st_LoadPs/x_MaxLimitReached": false,
            "st_LoadSb/i_Load": 500,
            "st_LoadSb/x_Failure": false,
            "st_LoadSb/i_MaxLoadSetting": 400,
            "st_LoadSb/x_MaxLimitReached": true
        }""",
    )
    await asyncio.sleep(0.1)
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
                    "id": "main-checkstay-deflector-load-alarm",
                    "active": True,
                    "thresholdValue": 4.0,
                    "actualValue": 5.0,
                },
                {
                    "id": "main-checkstay-sb-load-alarm",
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
    await asyncio.sleep(0.1)
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
    fo_payload = json.loads((Path(__file__).parent / "fo.json").read_text())
    await mqtt_client_send.publish(FiberOptic.TOPIC, json.dumps(fo_payload))
    await asyncio.sleep(0.1)
    response = await async_client.post(
        "/graphql",
        json={
            "query": """
            query {
                variables(variables: ["fiber-optic-main-v1-ps"]) {
                    id
                    variable {
                        id
                        name
                        unit
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
                    "id": "fiber-optic-main-v1-ps",
                    "variable": {
                        "id": "fiber-optic-main-v1-ps",
                        "name": "V1 PT",
                        "unit": "tonne",
                    },
                    "actual": {
                        "id": "fiber-optic-main-v1-ps",
                        "value": fo_payload["mm-rigging-load-v1-port"],
                    },
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
