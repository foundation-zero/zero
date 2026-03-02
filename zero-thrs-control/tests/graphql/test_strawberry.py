from asyncio import create_task, sleep
from datetime import datetime
from unittest.mock import Mock
from aiomqtt import Client as MqttClient
from httpx import ASGITransport, AsyncClient
import pytest
from thrs.cli.simulation_controls import (
    ControlModeMessage,
    SimulationInputMessage,
    SimulationStatusMessage,
)
from thrs.control.modules.consumers import ConsumersParameters
from thrs.control.modules.pcm import PcmParameters
from thrs.control.modules.pvt import PvtControlMode, PvtParameters
from thrs.control.modules.pvt_group import PvtGroupControlMode
from thrs.control.modules.thrusters import ThrustersControlMode, ThrustersParameters
from thrs.control.switching import SwitchingControlMode
from thrs.graphql import simulation
from thrs.graphql.base import ThrustersMessaging
from thrs.graphql.messaging import ControlMessaging, Messaging, SimulationMessaging
from thrs.graphql.strawberry import (
    app,
    consumers_messaging,
    messaging,
    pcm_messaging,
    pvt_messaging,
    simulation_messaging,
    thrusters_messaging,
)

from thrs.input_output.modules.consumers import (
    ConsumersControlValues,
    ConsumersSensorValues,
)
from thrs.input_output.modules.pcm import (
    PcmControlValues,
    PcmSensorValues,
)
from thrs.input_output.modules.pvt import (
    PvtControlValues,
    PvtSensorValues,
)
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)


@pytest.fixture
async def async_client():
    async with AsyncClient(
        base_url="http://test", transport=ASGITransport(app)
    ) as client:
        yield client


async def override_thrusters_messaging():
    mock = Mock(ControlMessaging)
    mock.sensor_values = ThrustersSensorValues.zero()
    mock.control_values = ThrustersControlValues.zero()
    mock.parameters = ThrustersParameters()
    mock.control_mode = ControlModeMessage(
        module="thrusters",
        mode=SwitchingControlMode(automatic_mode=ThrustersControlMode(mode="idle")),
    )

    async def wait(condition, *_args, timeout):
        return None

    mock.wait_for_control_mode.side_effect = wait
    mock.wait_for_control_values.side_effect = wait
    mock.wait_for_parameters.side_effect = wait
    return mock


async def override_pvt_messaging():
    mock = Mock(ControlMessaging)
    mock.sensor_values = PvtSensorValues.zero()
    mock.control_values = PvtControlValues.zero()
    mock.parameters = PvtParameters()
    mock.control_mode = ControlModeMessage(
        module="pvt",
        mode=SwitchingControlMode(
            automatic_mode=PvtControlMode(
                aft=PvtGroupControlMode(mode="idle"),
                fwd=PvtGroupControlMode(mode="idle"),
                owners=PvtGroupControlMode(mode="idle"),
            )
        ),
    )

    async def wait(condition, *_args, timeout):
        return None

    mock.wait_for_control_mode.side_effect = wait
    mock.wait_for_control_values.side_effect = wait
    mock.wait_for_parameters.side_effect = wait
    return mock


async def override_pcm_messaging():
    mock = Mock(ControlMessaging)
    mock.sensor_values = PcmSensorValues.zero()
    mock.control_values = PcmControlValues.zero()
    mock.parameters = PcmParameters()
    mock.control_mode = ControlModeMessage(
        module="pcm", mode=SwitchingControlMode(automatic_mode=None)
    )

    async def wait(condition, *_args, timeout):
        return None

    mock.wait_for_control_mode.side_effect = wait
    mock.wait_for_control_values.side_effect = wait
    mock.wait_for_parameters.side_effect = wait
    return mock


async def override_consumers_messaging():
    mock = Mock(ControlMessaging)
    mock.sensor_values = ConsumersSensorValues.zero()
    mock.control_values = ConsumersControlValues.zero()
    mock.parameters = ConsumersParameters()
    mock.control_mode = ControlModeMessage(
        module="consumers", mode=SwitchingControlMode(automatic_mode=None)
    )

    async def wait(condition, *_args, timeout):
        return None

    mock.wait_for_control_mode.side_effect = wait
    mock.wait_for_control_values.side_effect = wait
    mock.wait_for_parameters.side_effect = wait
    return mock


async def override_messaging():
    mock = Mock(Messaging)
    mock.simulation_status = SimulationStatusMessage(
        mode="thrusters",
        status="available",
        simulation_time=datetime.fromtimestamp(0),
        control_modules=["thrusters"],
    )

    async def wait(condition, *_args, timeout):
        return None

    mock.wait_for_simulation_status.side_effect = wait
    return mock


async def override_simulation_messaging():
    mock = Mock(SimulationMessaging)
    mock.mode = "thrusters"
    mock.simulation_inputs = ThrustersSimulationInputs.zero()
    mock.simulation_outputs = ThrustersSimulationOutputs.zero()

    async def wait(condition, *_args, timeout):
        return None

    mock.wait_for_simulation_inputs = wait
    return mock


async def test_query_sensor_values(async_client):
    app.dependency_overrides[messaging] = override_messaging
    app.dependency_overrides[thrusters_messaging] = override_thrusters_messaging
    app.dependency_overrides[pvt_messaging] = override_pvt_messaging
    app.dependency_overrides[pcm_messaging] = override_pcm_messaging
    app.dependency_overrides[consumers_messaging] = override_consumers_messaging
    app.dependency_overrides[simulation_messaging] = override_simulation_messaging
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
    app.dependency_overrides[simulation_messaging] = override_simulation_messaging
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
    app.dependency_overrides[simulation_messaging] = override_simulation_messaging
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


async def test_query_control_mode(async_client):
    app.dependency_overrides[messaging] = override_messaging
    app.dependency_overrides[thrusters_messaging] = override_thrusters_messaging
    app.dependency_overrides[pvt_messaging] = override_pvt_messaging
    app.dependency_overrides[pcm_messaging] = override_pcm_messaging
    app.dependency_overrides[consumers_messaging] = override_consumers_messaging
    app.dependency_overrides[simulation_messaging] = override_simulation_messaging
    response = await async_client.post(
        "/graphql",
        json={
            "query": """{
                modules {
                    thrusters {
                        controlMode {
                            automatic
                            automaticMode {
                                mode
                            }
                        }
                    }
                    pvt {
                        controlMode {
                            automatic
                            automaticMode {
                                fwd {
                                    mode
                                }
                                aft {
                                    mode
                                }
                                owners {
                                    mode
                                }
                            }
                        }
                    }
                    pcm {
                        controlMode {
                            automatic
                            automaticMode{
                                mode}
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
                    "controlMode": {
                        "automatic": True,
                        "automaticMode": {"mode": "idle"},
                    },
                },
                "pvt": {
                    "controlMode": {
                        "automatic": True,
                        "automaticMode": {
                            "fwd": {"mode": "idle"},
                            "aft": {"mode": "idle"},
                            "owners": {"mode": "idle"},
                        },
                    },
                },
                "pcm": {
                    "controlMode": {
                        "automatic": False,
                        "automaticMode": None,
                    },
                },
            }
        }
    }


async def test_query_simulation_inputs(async_client):
    app.dependency_overrides[messaging] = override_messaging
    app.dependency_overrides[thrusters_messaging] = override_thrusters_messaging
    app.dependency_overrides[pvt_messaging] = override_pvt_messaging
    app.dependency_overrides[pcm_messaging] = override_pcm_messaging
    app.dependency_overrides[consumers_messaging] = override_consumers_messaging
    app.dependency_overrides[simulation_messaging] = override_simulation_messaging
    response = await async_client.post(
        "/graphql",
        json={
            "query": """{
                simulation {
                    inputs {
                        ... on ThrustersSimulationInputsType {
                            thrustersAft {
                                active {
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
        "data": {"simulation": {"inputs": {"thrustersAft": {"active": {"value": 0.0}}}}}
    }


async def _mqtt_client(settings):
    async with MqttClient(settings.mqtt_host, settings.mqtt_port) as client:
        yield client


mqtt_client = pytest.fixture(_mqtt_client)
mqtt_client2 = pytest.fixture(_mqtt_client)


async def test_query_simulation_inputs_actual(async_client, mqtt_client, mqtt_client2):
    thrusters_msg: ThrustersMessaging = ControlMessaging(
        "thrusters",
        ThrustersSensorValues,
        ThrustersControlValues,
        ThrustersParameters,
        ThrustersControlMode,
        mqtt_client,
    )
    simulation_msg = SimulationMessaging(simulation.io_mapping, mqtt_client)
    msg = Messaging(mqtt_client, [thrusters_msg], simulation_msg)
    app.dependency_overrides[messaging] = lambda: msg
    app.dependency_overrides[thrusters_messaging] = lambda: thrusters_msg
    app.dependency_overrides[pvt_messaging] = override_pvt_messaging
    app.dependency_overrides[pcm_messaging] = override_pcm_messaging
    app.dependency_overrides[consumers_messaging] = override_consumers_messaging
    app.dependency_overrides[simulation_messaging] = lambda: simulation_msg

    await mqtt_client2.publish("thrs/simulation/inputs", None, qos=1, retain=True)
    await mqtt_client2.publish("thrs/simulation/status", None, qos=1, retain=True)

    run_task = create_task(await msg.run())
    try:
        # Simulation should be able to handle some time skew between status and inputs
        await mqtt_client2.publish(
            "thrs/simulation/inputs",
            SimulationInputMessage[ThrustersSimulationInputs](
                inputs=ThrustersSimulationInputs.zero()
            ).model_dump_json(),
        )
        await sleep(0.1)
        await mqtt_client2.publish(
            "thrs/simulation/status",
            SimulationStatusMessage(
                mode="thrusters",
                status="available",
                simulation_time=datetime.fromtimestamp(0),
                control_modules=["thrusters"],
            ).model_dump_json(),
        )
        await sleep(0.1)

        response = await async_client.post(
            "/graphql",
            json={
                "query": """{
                    simulation {
                        inputs {
                            ... on ThrustersSimulationInputsType {
                                thrustersAft {
                                    active {
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
                "simulation": {"inputs": {"thrustersAft": {"active": {"value": 0.0}}}}
            }
        }
    finally:
        run_task.cancel()


async def test_query_simulation_outputs(async_client):
    app.dependency_overrides[messaging] = override_messaging
    app.dependency_overrides[thrusters_messaging] = override_thrusters_messaging
    app.dependency_overrides[pvt_messaging] = override_pvt_messaging
    app.dependency_overrides[pcm_messaging] = override_pcm_messaging
    app.dependency_overrides[consumers_messaging] = override_consumers_messaging

    sim = await override_simulation_messaging()
    sim.simulation_outputs.thrusters_module_return.flow.value = 10.0  # type: ignore
    app.dependency_overrides[simulation_messaging] = lambda: sim

    response = await async_client.post(
        "/graphql",
        json={
            "query": """{
                simulation {
                    outputs {
                        ... on ThrustersSimulationOutputsType {
                            thrustersModuleReturn {
                                flow {
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
            "simulation": {
                "outputs": {"thrustersModuleReturn": {"flow": {"value": 10.0}}}
            }
        }
    }


async def test_query_simulation_state(async_client):
    app.dependency_overrides[messaging] = override_messaging
    app.dependency_overrides[thrusters_messaging] = override_thrusters_messaging
    app.dependency_overrides[pvt_messaging] = override_pvt_messaging
    app.dependency_overrides[pcm_messaging] = override_pcm_messaging
    app.dependency_overrides[consumers_messaging] = override_consumers_messaging
    app.dependency_overrides[simulation_messaging] = override_simulation_messaging
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
    app.dependency_overrides[thrusters_messaging] = override_thrusters_messaging
    app.dependency_overrides[pvt_messaging] = override_pvt_messaging
    app.dependency_overrides[pcm_messaging] = override_pcm_messaging
    app.dependency_overrides[consumers_messaging] = override_consumers_messaging
    app.dependency_overrides[simulation_messaging] = override_simulation_messaging
    response = await async_client.post(
        "/graphql",
        json={
            "query": """query {
            modules {
                thrusters {
                    controlMode {
                        automatic
                    }
                }
            }
        }"""
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "data": {"modules": {"thrusters": {"controlMode": {"automatic": True}}}}
    }


async def test_mutation_simulation_play(async_client):
    messaging_mock = await override_messaging()
    app.dependency_overrides[messaging] = lambda: messaging_mock
    app.dependency_overrides[thrusters_messaging] = override_thrusters_messaging
    app.dependency_overrides[pvt_messaging] = override_pvt_messaging
    app.dependency_overrides[pcm_messaging] = override_pcm_messaging
    app.dependency_overrides[consumers_messaging] = override_consumers_messaging
    app.dependency_overrides[simulation_messaging] = override_simulation_messaging

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
        mode="thrusters",
        status="running",
        simulation_time=datetime.fromtimestamp(0),
        control_modules=["thrusters"],
    )
    app.dependency_overrides[messaging] = lambda: messaging_mock
    app.dependency_overrides[thrusters_messaging] = override_thrusters_messaging
    app.dependency_overrides[pvt_messaging] = override_pvt_messaging
    app.dependency_overrides[pcm_messaging] = override_pcm_messaging
    app.dependency_overrides[consumers_messaging] = override_consumers_messaging
    app.dependency_overrides[simulation_messaging] = override_simulation_messaging

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
    app.dependency_overrides[simulation_messaging] = override_simulation_messaging
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
    app.dependency_overrides[simulation_messaging] = override_simulation_messaging
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


async def test_mutation_control_set_automation_mode(async_client):
    app.dependency_overrides[messaging] = override_messaging
    messaging_mock = await override_thrusters_messaging()
    app.dependency_overrides[thrusters_messaging] = lambda: messaging_mock
    app.dependency_overrides[pvt_messaging] = override_pvt_messaging
    app.dependency_overrides[pcm_messaging] = override_pcm_messaging
    app.dependency_overrides[consumers_messaging] = override_consumers_messaging
    app.dependency_overrides[simulation_messaging] = override_simulation_messaging

    response = await async_client.post(
        "/graphql",
        json={
            "query": """mutation {
                thrustersSetAutomationMode(automatic: true)
            }"""
        },
    )
    assert response.status_code == 200
    assert response.json() == {"data": {"thrustersSetAutomationMode": True}}
    messaging_mock.set_automation_mode.assert_awaited_once_with(True)


async def test_mutation_control_values_hanging_around(async_client):
    messaging_mock = await override_messaging()
    app.dependency_overrides[messaging] = lambda: messaging_mock
    app.dependency_overrides[thrusters_messaging] = override_thrusters_messaging
    app.dependency_overrides[pvt_messaging] = override_pvt_messaging
    app.dependency_overrides[pcm_messaging] = override_pcm_messaging
    app.dependency_overrides[consumers_messaging] = override_consumers_messaging
    app.dependency_overrides[simulation_messaging] = override_simulation_messaging

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
    app.dependency_overrides[simulation_messaging] = override_simulation_messaging

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
    simulation_mock = await override_simulation_messaging()
    app.dependency_overrides[messaging] = override_messaging
    app.dependency_overrides[thrusters_messaging] = override_thrusters_messaging
    app.dependency_overrides[pvt_messaging] = override_pvt_messaging
    app.dependency_overrides[pcm_messaging] = override_pcm_messaging
    app.dependency_overrides[consumers_messaging] = override_consumers_messaging
    app.dependency_overrides[simulation_messaging] = lambda: simulation_mock

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
    simulation_mock.set_simulation_inputs.assert_awaited_once()
    inputs = simulation_mock.set_simulation_inputs.call_args[0][0]
    assert inputs.thrusters_aft.heat_flow.value == 99.0
