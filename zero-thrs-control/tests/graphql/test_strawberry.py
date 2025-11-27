from datetime import datetime
from unittest.mock import Mock
from httpx import ASGITransport, AsyncClient
import pytest
from thrs.cli.simulation_controls import ControlStatusMessage, SimulationStatusMessage
from thrs.control.modules.consumers import ConsumersParameters
from thrs.control.modules.pcm import PcmParameters
from thrs.control.modules.pvt import PvtParameters
from thrs.control.modules.thrusters import ThrustersParameters
from thrs.graphql.messaging import Messaging, MessagingModule
from thrs.graphql.strawberry import (
    app,
    consumers_messaging,
    messaging,
    pcm_messaging,
    pvt_messaging,
    thrusters_messaging,
)

from thrs.input_output.modules.consumers import (
    ConsumersControlValues,
    ConsumersSensorValues,
    ConsumersSimulationInputs,
)
from thrs.input_output.modules.pcm import (
    PcmControlValues,
    PcmSensorValues,
    PcmSimulationInputs,
)
from thrs.input_output.modules.pvt import (
    PvtControlValues,
    PvtSensorValues,
    PvtSimulationInputs,
)
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


async def override_thrusters_messaging():
    mock = Mock(MessagingModule)
    mock.sensor_values = ThrustersSensorValues.zero()
    mock.control_values = ThrustersControlValues.zero()
    mock.parameters = ThrustersParameters()

    mock.simulation_inputs = ThrustersSimulationInputs.zero()

    async def wait(condition, *_args, timeout):
        return None

    mock.wait_for_control_values.side_effect = wait
    mock.wait_for_parameters.side_effect = wait
    mock.wait_for_simulation_inputs.side_effect = wait
    return mock


async def override_pvt_messaging():
    mock = Mock(MessagingModule)
    mock.sensor_values = PvtSensorValues.zero()
    mock.control_values = PvtControlValues.zero()
    mock.parameters = PvtParameters()

    mock.simulation_inputs = PvtSimulationInputs.zero()

    async def wait(condition, *_args, timeout):
        return None

    mock.wait_for_control_values.side_effect = wait
    mock.wait_for_parameters.side_effect = wait
    mock.wait_for_simulation_inputs.side_effect = wait
    return mock


async def override_pcm_messaging():
    mock = Mock(MessagingModule)
    mock.sensor_values = PcmSensorValues.zero()
    mock.control_values = PcmControlValues.zero()
    mock.parameters = PcmParameters()

    mock.simulation_inputs = PcmSimulationInputs.zero()

    async def wait(condition, *_args, timeout):
        return None

    mock.wait_for_control_values.side_effect = wait
    mock.wait_for_parameters.side_effect = wait
    mock.wait_for_simulation_inputs.side_effect = wait
    return mock


async def override_consumers_messaging():
    mock = Mock(MessagingModule)
    mock.sensor_values = ConsumersSensorValues.zero()
    mock.control_values = ConsumersControlValues.zero()
    mock.parameters = ConsumersParameters()

    mock.simulation_inputs = ConsumersSimulationInputs.zero()

    async def wait(condition, *_args, timeout):
        return None

    mock.wait_for_control_values.side_effect = wait
    mock.wait_for_parameters.side_effect = wait
    mock.wait_for_simulation_inputs.side_effect = wait
    return mock


async def override_messaging():
    mock = Mock(Messaging)
    mock.simulation_status = SimulationStatusMessage(
        status="available",
        simulation_time=datetime.fromtimestamp(0),
        module="thrusters",
    )
    mock.control_status = ControlStatusMessage(automatic=False)

    async def wait(condition, *_args, timeout):
        return None

    mock.wait_for_control_status.side_effect = wait
    mock.wait_for_simulation_status.side_effect = wait
    return mock


async def test_query_sensor_values(async_client):
    app.dependency_overrides[messaging] = override_messaging
    app.dependency_overrides[thrusters_messaging] = override_thrusters_messaging
    app.dependency_overrides[pvt_messaging] = override_pvt_messaging
    app.dependency_overrides[pcm_messaging] = override_pcm_messaging
    app.dependency_overrides[consumers_messaging] = override_consumers_messaging
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
    app.dependency_overrides[thrusters_messaging] = override_thrusters_messaging
    app.dependency_overrides[pvt_messaging] = override_pvt_messaging
    app.dependency_overrides[pcm_messaging] = override_pcm_messaging
    app.dependency_overrides[consumers_messaging] = override_consumers_messaging
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
    app.dependency_overrides[thrusters_messaging] = override_thrusters_messaging
    app.dependency_overrides[pvt_messaging] = override_pvt_messaging
    app.dependency_overrides[pcm_messaging] = override_pcm_messaging
    app.dependency_overrides[consumers_messaging] = override_consumers_messaging
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
    app.dependency_overrides[thrusters_messaging] = override_thrusters_messaging
    app.dependency_overrides[pvt_messaging] = override_pvt_messaging
    app.dependency_overrides[pcm_messaging] = override_pcm_messaging
    app.dependency_overrides[consumers_messaging] = override_consumers_messaging
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
    thrusters = await override_thrusters_messaging()
    app.dependency_overrides[thrusters_messaging] = lambda: thrusters
    app.dependency_overrides[pvt_messaging] = override_pvt_messaging
    app.dependency_overrides[pcm_messaging] = override_pcm_messaging
    app.dependency_overrides[consumers_messaging] = override_consumers_messaging

    thrusters.simulation_outputs.thrusters_module_return.flow.value = 10.0  # type: ignore

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
                        "outputs": {"thrustersModuleReturn": {"flow": {"value": 10.0}}}
                    }
                }
            }
        }
    }


async def test_query_simulation_state(async_client):
    app.dependency_overrides[messaging] = override_messaging
    app.dependency_overrides[thrusters_messaging] = override_thrusters_messaging
    app.dependency_overrides[pvt_messaging] = override_pvt_messaging
    app.dependency_overrides[pcm_messaging] = override_pcm_messaging
    app.dependency_overrides[consumers_messaging] = override_consumers_messaging
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
    app.dependency_overrides[thrusters_messaging] = override_thrusters_messaging
    app.dependency_overrides[pvt_messaging] = override_pvt_messaging
    app.dependency_overrides[pcm_messaging] = override_pcm_messaging
    app.dependency_overrides[consumers_messaging] = override_consumers_messaging
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
    app.dependency_overrides[thrusters_messaging] = override_thrusters_messaging
    app.dependency_overrides[pvt_messaging] = override_pvt_messaging
    app.dependency_overrides[pcm_messaging] = override_pcm_messaging
    app.dependency_overrides[consumers_messaging] = override_consumers_messaging

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
        status="running", simulation_time=datetime.fromtimestamp(0), module="thrusters"
    )
    app.dependency_overrides[messaging] = lambda: messaging_mock
    app.dependency_overrides[thrusters_messaging] = override_thrusters_messaging
    app.dependency_overrides[pvt_messaging] = override_pvt_messaging
    app.dependency_overrides[pcm_messaging] = override_pcm_messaging
    app.dependency_overrides[consumers_messaging] = override_consumers_messaging

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
    app.dependency_overrides[thrusters_messaging] = override_thrusters_messaging
    app.dependency_overrides[pvt_messaging] = override_pvt_messaging
    app.dependency_overrides[pcm_messaging] = override_pcm_messaging
    app.dependency_overrides[consumers_messaging] = override_consumers_messaging

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
    thrusters_mock = await override_thrusters_messaging()
    app.dependency_overrides[messaging] = override_messaging
    app.dependency_overrides[thrusters_messaging] = lambda: thrusters_mock
    app.dependency_overrides[pvt_messaging] = override_pvt_messaging
    app.dependency_overrides[pcm_messaging] = override_pcm_messaging
    app.dependency_overrides[consumers_messaging] = override_consumers_messaging

    response = await async_client.post(
        "/graphql",
        json={
            "query": """mutation {
                thrustersControlSetThrustersPump1(component: {dutypoint: 0.5, on:true}) {
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
            "thrustersControlSetThrustersPump1": {
                "thrustersPump1": {"dutypoint": {"value": 0.5}}
            }
        }
    }
    thrusters_mock.send_manual_controls.assert_awaited_once()
    control_values = thrusters_mock.send_manual_controls.call_args[0][0]
    assert control_values.thrusters_pump_1.dutypoint.value == 0.5
    assert control_values.thrusters_pump_1.on.value


async def test_mutation_simulation_input(async_client):
    app.dependency_overrides[messaging] = override_messaging
    app.dependency_overrides[thrusters_messaging] = override_thrusters_messaging
    app.dependency_overrides[pvt_messaging] = override_pvt_messaging
    app.dependency_overrides[pcm_messaging] = override_pcm_messaging
    app.dependency_overrides[consumers_messaging] = override_consumers_messaging
    response = await async_client.post(
        "/graphql",
        json={
            "query": """mutation {
                thrustersSimulationSetThrustersAft(component: {heatFlow: 0.0, active: false}) {
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
            "thrustersSimulationSetThrustersAft": {
                "thrustersAft": {"active": {"value": False}}
            }
        }
    }


async def test_mutation_control_set_automation_mode(async_client):
    messaging_mock = await override_messaging()
    app.dependency_overrides[messaging] = lambda: messaging_mock
    app.dependency_overrides[thrusters_messaging] = override_thrusters_messaging
    app.dependency_overrides[pvt_messaging] = override_pvt_messaging
    app.dependency_overrides[pcm_messaging] = override_pcm_messaging
    app.dependency_overrides[consumers_messaging] = override_consumers_messaging

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
    app.dependency_overrides[thrusters_messaging] = override_thrusters_messaging
    app.dependency_overrides[pvt_messaging] = override_pvt_messaging
    app.dependency_overrides[pcm_messaging] = override_pcm_messaging
    app.dependency_overrides[consumers_messaging] = override_consumers_messaging

    await async_client.post(
        "/graphql",
        json={
            "query": """mutation {
                thrustersControlSetThrustersPump1(component: {dutypoint: 0.5, on:true}) {
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
                thrustersControlSetThrustersPump2(component: {dutypoint: 0.4, on:true}) {
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
            "thrustersControlSetThrustersPump2": {
                "thrustersPump1": {"dutypoint": {"value": 0}},
                "thrustersPump2": {"dutypoint": {"value": 0.4}},
            }
        }
    }


async def test_mutation_parameter(async_client):
    messaging_mock = await override_thrusters_messaging()
    app.dependency_overrides[thrusters_messaging] = lambda: messaging_mock
    app.dependency_overrides[pvt_messaging] = override_pvt_messaging
    app.dependency_overrides[messaging] = override_messaging
    app.dependency_overrides[pcm_messaging] = override_pcm_messaging
    app.dependency_overrides[consumers_messaging] = override_consumers_messaging

    response = await async_client.post(
        "/graphql",
        json={
            "query": """mutation {
                thrustersParameterSetCoolingFlow(value: 99.0) {
                    coolingFlow
                }
            }"""
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "data": {"thrustersParameterSetCoolingFlow": {"coolingFlow": 99.0}}
    }
    messaging_mock.set_parameters.assert_awaited_once()
    parameters = messaging_mock.set_parameters.call_args[0][0]
    assert parameters.cooling_flow == 99.0


async def test_mutation_set_simulation_inputs(async_client):
    messaging_mock = await override_thrusters_messaging()
    app.dependency_overrides[thrusters_messaging] = lambda: messaging_mock
    app.dependency_overrides[pvt_messaging] = override_pvt_messaging
    app.dependency_overrides[pcm_messaging] = override_pcm_messaging
    app.dependency_overrides[consumers_messaging] = override_consumers_messaging

    response = await async_client.post(
        "/graphql",
        json={
            "query": """mutation {
                thrustersSimulationSetThrustersAft(component: { heatFlow: 99.0, active: false }) {
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
            "thrustersSimulationSetThrustersAft": {
                "thrustersAft": {"heatFlow": {"value": 99.0}}
            }
        }
    }
    messaging_mock.set_simulation_inputs.assert_awaited_once()
    inputs = messaging_mock.set_simulation_inputs.call_args[0][0]
    assert inputs.thrusters_aft.heat_flow.value == 99.0
