from datetime import datetime
from unittest.mock import Mock
from httpx import ASGITransport, AsyncClient
import pytest
from thrs.cli.simulation_controls import ControlStatusMessage, SimulationStatusMessage
from thrs.control.modules.thrusters import ThrustersParameters
from thrs.graphql.messaging import Messaging
from thrs.graphql.strawberry import app, messaging

from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationInputs,
)


@pytest.fixture
async def async_client():
    async with AsyncClient(
        base_url="http://test", transport=ASGITransport(app)
    ) as client:
        yield client


async def override_messaging():
    mock = Mock(Messaging)
    mock.sensor_values = ThrustersSensorValues.zero()
    mock.control_values = ThrustersControlValues.zero()
    mock.parameters = ThrustersParameters()
    mock.simulation_status = SimulationStatusMessage(
        status="available", simulation_time=datetime.fromtimestamp(0)
    )
    mock.control_status = ControlStatusMessage(automatic=False)
    mock.simulation_inputs = ThrustersSimulationInputs.zero()

    async def wait(condition, *_args, timeout):
        return None

    mock.wait_for_simulation_status.side_effect = wait
    mock.wait_for_control_status.side_effect = wait
    mock.wait_for_control_values.side_effect = wait
    mock.wait_for_parameters.side_effect = wait
    mock.wait_for_simulation_inputs.side_effect = wait
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


async def test_query_parameters(async_client):
    app.dependency_overrides[messaging] = override_messaging
    response = await async_client.post(
        "/graphql",
        json={
            "query": """{
                modules {
                    thrusters {
                        parameters {
                            aftFlowBalanceTuning
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
                "thrusters": {"parameters": {"aftFlowBalanceTuning": [0.01, 0.001, 0]}}
            }
        }
    }


async def test_query_simulation_inputs(async_client):
    app.dependency_overrides[messaging] = override_messaging
    response = await async_client.post(
        "/graphql",
        json={
            "query": """{
                modules {
                    thrusters {
                        simulation {
                            inputs {
                                thrustersAft {
                                    active {
                                        value
                                    }
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
                    "simulation": {
                        "inputs": {"thrustersAft": {"active": {"value": 0.0}}}
                    }
                }
            }
        }
    }


async def test_query_simulation_outputs(async_client):
    app.dependency_overrides[messaging] = override_messaging
    response = await async_client.post(
        "/graphql",
        json={
            "query": """{
                modules {
                    thrusters {
                        simulation {
                            outputs {
                                thrustersModuleReturn {
                                    flow {
                                        value
                                    }
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
                    "simulation": {
                        "outputs": {"thrustersModuleReturn": {"flow": {"value": 0.0}}}
                    }
                }
            }
        }
    }


async def test_query_simulation_state(async_client):
    app.dependency_overrides[messaging] = override_messaging
    response = await async_client.post(
        "/graphql",
        json={
            "query": """query {
            simulation {
                status
            }
        }"""
        },
    )

    assert response.status_code == 200
    assert response.json() == {"data": {"simulation": {"status": "available"}}}


async def test_query_control_automation_mode(async_client):
    app.dependency_overrides[messaging] = override_messaging
    response = await async_client.post(
        "/graphql",
        json={
            "query": """query {
            control {
                automatic
            }
        }"""
        },
    )

    assert response.status_code == 200
    assert response.json() == {"data": {"control": {"automatic": False}}}


async def test_mutation_simulation_play(async_client):
    messaging_mock = await override_messaging()
    app.dependency_overrides[messaging] = lambda: messaging_mock

    response = await async_client.post(
        "/graphql",
        json={
            "query": """mutation {
                simulationPlay(playbackRate: 1.0)
            }"""
        },
    )
    assert response.status_code == 200
    assert response.json() == {"data": {"simulationPlay": None}}
    messaging_mock.play_simulation.assert_awaited_once_with(1.0)


async def test_mutation_simulation_pause(async_client):
    messaging_mock = await override_messaging()
    messaging_mock.simulation_status = SimulationStatusMessage(
        status="running", simulation_time=datetime.fromtimestamp(0)
    )
    app.dependency_overrides[messaging] = lambda: messaging_mock

    response = await async_client.post(
        "/graphql",
        json={
            "query": """mutation {
                simulationPause
            }"""
        },
    )
    assert response.status_code == 200
    assert response.json() == {"data": {"simulationPause": None}}
    messaging_mock.pause_simulation.assert_awaited_once()


async def test_mutation_simulation_step(async_client):
    messaging_mock = await override_messaging()
    app.dependency_overrides[messaging] = lambda: messaging_mock

    response = await async_client.post(
        "/graphql",
        json={
            "query": """mutation {
                simulationStep(seconds: 2.0)
            }"""
        },
    )
    assert response.status_code == 200
    assert response.json() == {"data": {"simulationStep": None}}
    messaging_mock.step_simulation.assert_awaited_once_with(2.0)


async def test_mutation_control_value(async_client):
    messaging_mock = await override_messaging()
    app.dependency_overrides[messaging] = lambda: messaging_mock

    response = await async_client.post(
        "/graphql",
        json={
            "query": """mutation {
                setThrustersControlThrustersPump1(component: {dutypoint: 0.5, on:true}) {
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
        "data": {
            "setThrustersControlThrustersPump1": {
                "thrustersPump1": {"dutypoint": {"value": 0.5}}
            }
        }
    }
    messaging_mock.send_manual_controls.assert_awaited_once()
    control_values = messaging_mock.send_manual_controls.call_args[0][0]
    assert control_values.thrusters_pump_1.dutypoint.value == 0.5
    assert control_values.thrusters_pump_1.on.value


async def test_mutation_simulation_input(async_client):
    app.dependency_overrides[messaging] = override_messaging
    response = await async_client.post(
        "/graphql",
        json={
            "query": """mutation {
                setThrustersSimulationThrustersAft(component: {heatFlow: 0.0, active: false}) {
                    thrustersAft {
                        active {
                            value
                        }
                    }
                }
            }"""
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "setThrustersSimulationThrustersAft": {
                "thrustersAft": {"active": {"value": False}}
            }
        }
    }


async def test_mutation_control_set_automation_mode(async_client):
    messaging_mock = await override_messaging()
    app.dependency_overrides[messaging] = lambda: messaging_mock

    response = await async_client.post(
        "/graphql",
        json={
            "query": """mutation {
                controlSetAutomationMode(automatic: true)
            }"""
        },
    )
    assert response.status_code == 200
    assert response.json() == {"data": {"controlSetAutomationMode": None}}
    messaging_mock.set_automation.assert_awaited_once_with(True)


async def test_mutation_control_values_hanging_around(async_client):
    messaging_mock = await override_messaging()
    app.dependency_overrides[messaging] = lambda: messaging_mock

    await async_client.post(
        "/graphql",
        json={
            "query": """mutation {
                setThrustersControlThrustersPump1(component: {dutypoint: 0.5, on:true}) {
                    thrustersPump1 {
                        dutypoint {
                            value
                        }
                    }
            }"""
        },
    )
    messaging_mock.control_values = ThrustersControlValues.zero()
    response2 = await async_client.post(
        "/graphql",
        json={
            "query": """mutation {
                setThrustersControlThrustersPump2(component: {dutypoint: 0.4, on:true}) {
                    thrustersPump1 {
                        dutypoint {
                            value
                        }
                    }
                    thrustersPump2 {
                        dutypoint {
                            value
                        }
                    }
                }
            }"""
        },
    )

    assert response2.json() == {
        "data": {
            "setThrustersControlThrustersPump2": {
                "thrustersPump1": {"dutypoint": {"value": 0}},
                "thrustersPump2": {"dutypoint": {"value": 0.4}},
            }
        }
    }


async def test_mutation_parameter(async_client):
    messaging_mock = await override_messaging()
    app.dependency_overrides[messaging] = lambda: messaging_mock

    response = await async_client.post(
        "/graphql",
        json={
            "query": """mutation {
                setThrustersParameterCoolingFlow(value: 99.0) {
                    coolingFlow
                }
            }"""
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "data": {"setThrustersParameterCoolingFlow": {"coolingFlow": 99.0}}
    }
    messaging_mock.set_parameters.assert_awaited_once()
    parameters = messaging_mock.set_parameters.call_args[0][0]
    assert parameters.cooling_flow == 99.0


async def test_mutation_set_simulation_inputs(async_client):
    messaging_mock = await override_messaging()
    app.dependency_overrides[messaging] = lambda: messaging_mock

    response = await async_client.post(
        "/graphql",
        json={
            "query": """mutation {
                setThrustersSimulationThrustersAft(component: { heatFlow: 99.0, active: false }) {
                    thrustersAft {
                        heatFlow {
                            value
                        }
                    }
                }
            }"""
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "setThrustersSimulationThrustersAft": {
                "thrustersAft": {"heatFlow": {"value": 99.0}}
            }
        }
    }
    messaging_mock.set_simulation_inputs.assert_awaited_once()
    inputs = messaging_mock.set_simulation_inputs.call_args[0][0]
    assert inputs.thrusters_aft.heat_flow.value == 99.0
