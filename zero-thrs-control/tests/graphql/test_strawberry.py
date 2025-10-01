from unittest.mock import Mock
from httpx import ASGITransport, AsyncClient
import pytest
from thrs.graphql.messaging import Messaging
from thrs.graphql.strawberry import app, messaging

from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
)


@pytest.fixture
async def async_client():
    async with AsyncClient(
        base_url="http://test",
        transport=ASGITransport(app)
    ) as client:
        yield client

async def override_messaging():
    mock = Mock(Messaging)
    mock.sensor_values = ThrustersSensorValues.zero()
    mock.control_values = ThrustersControlValues.zero()
    return mock


async def test_query_sensor_values(async_client):
    app.dependency_overrides[messaging] = override_messaging
    response = await async_client.post(
        "/graphql",
        json={
            "query": """{
                modules {
                    thrusters {
                        sensorValues {
                            thrustersPump1 {
                                speed {
                                    value
                                }
                            }
                        }
                    }
                }
            }"""
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "modules": {
                "thrusters": {
                    "sensorValues": {"thrustersPump1": {"speed": {"value": 0.0}}}
                }
            }
        }
    }


async def test_query_control_values(async_client):
    app.dependency_overrides[messaging] = override_messaging
    response = await async_client.post(
        "/graphql",
        json={
            "query": """{
                modules {
                    thrusters {
                        controlValues {
                            thrustersPump1 {
                                dutypoint {
                                    value
                                }
                            }
                        }
                    }
                }
            }"""
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "modules": {
                "thrusters": {
                    "controlValues": {"thrustersPump1": {"dutypoint": {"value": 0.0}}}
                }
            }
        }
    }


async def test_mutation_control_value(async_client):
    messaging_mock = await override_messaging()
    app.dependency_overrides[messaging] = lambda: messaging_mock

    response = await async_client.post(
        "/graphql",
        json={
            "query": """mutation {
                setThrustersPump1(component: {dutypoint: 0.5, on:true}) {
                    thrustersPump1 {
                        dutypoint {
                            value
                        }
                    }
                }
            }"""
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "data": {"setThrustersPump1": {"thrustersPump1": {"dutypoint": {"value": 0.5}}}}
    }
    messaging_mock.send_manual_controls.assert_awaited_once()
    control_values = messaging_mock.send_manual_controls.call_args[0][0]
    assert control_values.thrusters_pump_1.dutypoint.value == 0.5
    assert control_values.thrusters_pump_1.on.value
