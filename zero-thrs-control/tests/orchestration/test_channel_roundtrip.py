import asyncio
from asyncio import create_task
from datetime import datetime
from unittest import mock
from uuid import uuid4

from aiomqtt import Client as MqttClient

from thrs.control.switching import AutomationMode
from thrs.input_output.base import (
    CombinedValues,
    SimulationInputs,
    SimulationValues,
    ThrsValues,
)
from thrs.orchestration.comms import (
    ControlApiChannels,
    ControlApiChannelsDescription,
    ControlChannels,
    ControlChannelsDescription,
    DirectivesApiChannels,
    DirectivesApiChannelsDescription,
    DirectivesChannels,
    DirectivesChannelsDescription,
    MqttConnector,
    SimulationApiChannels,
    SimulationApiChannelsDescription,
    SimulationChannels,
    SimulationChannelsDescription,
)
from thrs.orchestration.config import Config
from thrs.orchestration.module import ModuleDescription
from thrs.runtime.messages import SimulationStatusMessage


class DemoSensorValues(ThrsValues):
    value: float = 0.0


class DemoComponent(ThrsValues):
    value: float = 0.0


class DemoControlValues(ThrsValues):
    command: DemoComponent = DemoComponent()


class DemoParameters(ThrsValues):
    value: float = 0.0


class DemoMode(ThrsValues):
    mode: str = "manual"


class DemoControllerState(ThrsValues):
    state: str = "ok"


class DemoSimulationInputs(SimulationInputs):
    target: float = 1.0


class DemoSimulationOutputs(SimulationValues):
    measured: float = 2.0


def _config() -> Config:
    return Config(
        mqtt_host="localhost",
        mqtt_port=1883,
        mqtt_devices_topic_prefix="thrs/devices",
        mqtt_controller_topic_prefix="thrs/controller",
        mqtt_simulation_topic_prefix="thrs/simulation",
        mqtt_control_topic_suffix="control",
        mqtt_controller_topic_suffix="set",
    )


def _listener_for_topic(connector: MqttConnector, topic: str):
    return next(
        listener
        for listener in connector.listeners
        if topic in listener.subscribe_topics()
    )


async def _wait_until(predicate, timeout_s: float = 2.0):
    async with asyncio.timeout(timeout_s):
        while not predicate():
            await asyncio.sleep(0.01)


async def test_control_channels_roundtrip_manual_values_with_suffix_split():
    mqtt_client = mock.AsyncMock()
    connector = MqttConnector(mqtt_client)

    channels, connector_run = await connector.run(
        ControlChannels,
        ControlChannelsDescription(
            devices_topic_prefix="thrs/devices",
            controller_topic_prefix="thrs/controller",
            sensor_values_clss={"thrusters": DemoSensorValues},
            control_values_clss={"thrusters": DemoControlValues},
            controller_state_clss={"thrusters": DemoControllerState},
            parameters_clss={"thrusters": DemoParameters},
            automation_modes_clss={"thrusters": AutomationMode},
            control_values_topic_suffix="control",
            controller_topic_suffix="set",
            automation_mode_clss={"thrusters": AutomationMode},
        ),
    )

    task = create_task(connector_run)
    try:
        value = DemoControlValues(command=DemoComponent(value=3.5))
        combined = CombinedValues(values={"thrusters": value})

        await channels.send_manual_control(combined)

        mqtt_client.publish.assert_any_call(
            "thrs/controller/thrusters/manual-values",
            mock.ANY,
            qos=1,
            retain=False,
        )

        listen_topic = "thrs/controller/thrusters/manual-values/set"
        _listener_for_topic(connector, listen_topic).handle_message(
            listen_topic,
            value.model_dump_json(by_alias=True),
        )

        got = channels.get_manual_controls()
        assert got is not None
        assert got.values["thrusters"] == value
    finally:
        task.cancel()


async def test_control_api_channels_roundtrip_manual_values_with_suffix_split():
    mqtt_client = mock.AsyncMock()
    connector = MqttConnector(mqtt_client)
    config = _config()

    module_description = ModuleDescription(
        DemoSensorValues,
        DemoControlValues,
        DemoParameters,
        lambda *_args, **_kwargs: mock.Mock(),
        DemoMode,
        DemoControllerState,
        lambda: mock.Mock(),
    )

    channels, connector_run = await connector.run(
        ControlApiChannels,
        ControlApiChannelsDescription.from_settings(
            config,
            module_name="thrusters",
            module_description=module_description,
            automation_mode_cls=AutomationMode,
        ),
    )
    task = create_task(connector_run)
    try:
        value = DemoControlValues(command=DemoComponent(value=7.25))
        await channels.send_manual_values(value)

        mqtt_client.publish.assert_any_call(
            "thrs/controller/thrusters/manual-values/set",
            mock.ANY,
            qos=1,
            retain=False,
        )

        listen_topic = "thrs/controller/thrusters/manual-values"
        _listener_for_topic(connector, listen_topic).handle_message(
            listen_topic,
            value.model_dump_json(by_alias=True),
        )

        assert channels.get_manual_values() == value
    finally:
        task.cancel()


async def test_simulation_api_channels_roundtrip_with_suffix_split():
    mqtt_client = mock.AsyncMock()
    connector = MqttConnector(mqtt_client)
    config = _config()

    channels, connector_run = await connector.run(
        SimulationApiChannels,
        SimulationApiChannelsDescription.from_settings(
            config,
            simulation_inputs_cls=DemoSimulationInputs,
            simulation_outputs_cls=DemoSimulationOutputs,
        ),
    )
    task = create_task(connector_run)
    try:
        value = DemoSimulationInputs(target=3.0)
        await channels.send_simulation_inputs(value)

        mqtt_client.publish.assert_any_call(
            "thrs/controller/simulation-inputs/set",
            mock.ANY,
            qos=1,
            retain=False,
        )

        in_topic = "thrs/controller/simulation-inputs"
        out_topic = "thrs/controller/simulation-outputs"
        _listener_for_topic(connector, in_topic).handle_message(
            in_topic,
            value.model_dump_json(by_alias=True),
        )
        _listener_for_topic(connector, out_topic).handle_message(
            out_topic,
            DemoSimulationOutputs(measured=4.0).model_dump_json(by_alias=True),
        )

        assert channels.get_simulation_inputs() == value
        assert channels.get_simulation_outputs() == DemoSimulationOutputs(measured=4.0)
    finally:
        task.cancel()


async def test_directives_api_channels_roundtrip_from_settings():
    mqtt_client = mock.AsyncMock()
    connector = MqttConnector(mqtt_client)
    config = _config()

    channels, connector_run = await connector.run(
        DirectivesApiChannels,
        DirectivesApiChannelsDescription.from_settings(config),
    )
    task = create_task(connector_run)
    try:
        await channels.send_play(1.5)
        mqtt_client.publish.assert_any_call(
            "thrs/controller/play",
            mock.ANY,
            qos=1,
            retain=False,
        )

        status = SimulationStatusMessage(
            mode="thrusters",
            status="available",
            control_modules=["thrusters"],
            simulation_time=datetime.fromtimestamp(0),
        )
        status_topic = "thrs/controller/status"
        _listener_for_topic(connector, status_topic).handle_message(
            status_topic,
            status.model_dump_json(by_alias=True),
        )

        assert channels.get_simulation_status() == status
    finally:
        task.cancel()


async def test_control_channels_to_control_api_channels_roundtrip_all_channels(
    settings,
):
    test_id = uuid4().hex[:8]
    devices_prefix = f"test_devices_topic/{test_id}"
    controller_prefix = f"test_controller_topic/{test_id}"

    async with (
        MqttClient(settings.mqtt_host, settings.mqtt_port) as control_client,
        MqttClient(settings.mqtt_host, settings.mqtt_port) as api_client,
    ):
        control_connector = MqttConnector(control_client)
        api_connector = MqttConnector(api_client)

        control_channels, control_run = await control_connector.run(
            ControlChannels,
            ControlChannelsDescription(
                devices_topic_prefix=devices_prefix,
                controller_topic_prefix=controller_prefix,
                sensor_values_clss={"thrusters": DemoSensorValues},
                control_values_clss={"thrusters": DemoControlValues},
                controller_state_clss={"thrusters": DemoControllerState},
                parameters_clss={"thrusters": DemoParameters},
                automation_modes_clss={"thrusters": AutomationMode},
                control_values_topic_suffix="control",
                controller_topic_suffix="set",
                automation_mode_clss={"thrusters": AutomationMode},
            ),
        )
        control_task = create_task(control_run)

        api_channels, api_run = await api_connector.run(
            ControlApiChannels,
            ControlApiChannelsDescription(
                module_name="thrusters",
                devices_topic_prefix=devices_prefix,
                controller_topic_prefix=controller_prefix,
                sensor_values_cls=DemoSensorValues,
                control_values_cls=DemoControlValues,
                controller_state_cls=DemoControllerState,
                parameters_cls=DemoParameters,
                control_modes_cls=AutomationMode,
                automation_mode_cls=AutomationMode,
                control_values_topic_suffix="control",
                controller_topic_suffix="set",
            ),
        )
        api_task = create_task(api_run)

        try:
            expected_control_values = DemoControlValues(
                command=DemoComponent(value=10.5)
            )
            expected_manual_values = DemoControlValues(
                command=DemoComponent(value=22.0)
            )
            expected_parameters = DemoParameters(value=3.14)
            expected_state = DemoControllerState(state="running")
            expected_mode = AutomationMode(mode="automatic")

            await control_channels.send_control_values(
                CombinedValues(values={"thrusters": expected_control_values})
            )
            await control_channels.send_manual_control(
                CombinedValues(values={"thrusters": expected_manual_values})
            )
            await control_channels.send_parameters(
                CombinedValues(values={"thrusters": expected_parameters})
            )
            await control_channels.send_controller_state(
                CombinedValues(values={"thrusters": expected_state})
            )
            await control_channels.send_control_modes(
                CombinedValues(values={"thrusters": expected_mode})
            )

            await _wait_until(
                lambda: api_channels.get_control_values() == expected_control_values
                and api_channels.get_manual_values() == expected_manual_values
                and api_channels.get_parameters() == expected_parameters
                and api_channels.get_controller_state() == expected_state
                and api_channels.get_control_modes() == expected_mode
            )
        finally:
            control_task.cancel()
            api_task.cancel()


async def test_control_api_channels_to_control_channels_roundtrip_shared_channels(
    settings,
):
    test_id = uuid4().hex[:8]
    devices_prefix = f"test_devices_topic/{test_id}"
    controller_prefix = f"test_controller_topic/{test_id}"

    async with (
        MqttClient(settings.mqtt_host, settings.mqtt_port) as control_client,
        MqttClient(settings.mqtt_host, settings.mqtt_port) as api_client,
    ):
        control_connector = MqttConnector(control_client)
        api_connector = MqttConnector(api_client)

        control_channels, control_run = await control_connector.run(
            ControlChannels,
            ControlChannelsDescription(
                devices_topic_prefix=devices_prefix,
                controller_topic_prefix=controller_prefix,
                sensor_values_clss={"thrusters": DemoSensorValues},
                control_values_clss={"thrusters": DemoControlValues},
                controller_state_clss={"thrusters": DemoControllerState},
                parameters_clss={"thrusters": DemoParameters},
                automation_modes_clss={"thrusters": AutomationMode},
                control_values_topic_suffix="control",
                controller_topic_suffix="set",
                automation_mode_clss={"thrusters": AutomationMode},
            ),
        )
        control_task = create_task(control_run)

        api_channels, api_run = await api_connector.run(
            ControlApiChannels,
            ControlApiChannelsDescription(
                module_name="thrusters",
                devices_topic_prefix=devices_prefix,
                controller_topic_prefix=controller_prefix,
                sensor_values_cls=DemoSensorValues,
                control_values_cls=DemoControlValues,
                controller_state_cls=DemoControllerState,
                parameters_cls=DemoParameters,
                control_modes_cls=AutomationMode,
                automation_mode_cls=AutomationMode,
                control_values_topic_suffix="control",
                controller_topic_suffix="set",
            ),
        )
        api_task = create_task(api_run)

        try:
            expected_manual_values = DemoControlValues(
                command=DemoComponent(value=12.0)
            )
            expected_parameters = DemoParameters(value=8.5)
            expected_mode = AutomationMode(mode="automatic")

            await api_channels.send_manual_values(expected_manual_values)
            await api_channels.send_parameters(expected_parameters)
            await api_channels.send_automation_modes(expected_mode)

            await _wait_until(
                lambda: control_channels.get_manual_controls() is not None
                and control_channels.get_parameters() is not None
                and control_channels.get_automation_modes() is not None
                and "thrusters" in control_channels.get_automation_modes().values
            )

            manual_values = control_channels.get_manual_controls()
            parameters = control_channels.get_parameters()
            automation_modes = control_channels.get_automation_modes()

            assert manual_values is not None
            assert parameters is not None
            assert automation_modes is not None

            assert manual_values.values["thrusters"] == expected_manual_values
            assert parameters.values["thrusters"] == expected_parameters
            assert automation_modes.values["thrusters"] == expected_mode
        finally:
            control_task.cancel()
            api_task.cancel()


async def test_simulation_channels_to_simulation_api_channels_roundtrip_all_channels(
    settings,
):
    test_id = uuid4().hex[:8]
    devices_prefix = f"test_devices_topic/{test_id}"
    controller_prefix = f"test_controller_topic/{test_id}"

    async with (
        MqttClient(settings.mqtt_host, settings.mqtt_port) as simulation_client,
        MqttClient(settings.mqtt_host, settings.mqtt_port) as api_client,
    ):
        simulation_connector = MqttConnector(simulation_client)
        api_connector = MqttConnector(api_client)

        simulation_channels, simulation_run = await simulation_connector.run(
            SimulationChannels,
            SimulationChannelsDescription(
                devices_topic_prefix=devices_prefix,
                controller_topic_prefix=controller_prefix,
                sensor_values_clss={"thrusters": DemoSensorValues},
                control_values_clss={"thrusters": DemoControlValues},
                simulation_inputs_cls=DemoSimulationInputs,
                simulation_outputs_cls=DemoSimulationOutputs,
                control_values_topic_suffix="control",
                controller_topic_suffix="set",
            ),
        )
        simulation_task = create_task(simulation_run)

        api_channels, api_run = await api_connector.run(
            SimulationApiChannels,
            SimulationApiChannelsDescription(
                controller_topic_prefix=controller_prefix,
                controller_topic_suffix="set",
                simulation_inputs_cls=DemoSimulationInputs,
                simulation_outputs_cls=DemoSimulationOutputs,
            ),
        )
        api_task = create_task(api_run)

        try:
            sim_to_api_inputs = DemoSimulationInputs(target=10.0)
            sim_to_api_outputs = DemoSimulationOutputs(measured=21.0)
            api_to_sim_inputs = DemoSimulationInputs(target=42.0)

            await simulation_channels.send_simulation_inputs(sim_to_api_inputs)
            await simulation_channels.send_simulation_outputs(sim_to_api_outputs)

            await _wait_until(
                lambda: api_channels.get_simulation_inputs() == sim_to_api_inputs
                and api_channels.get_simulation_outputs() == sim_to_api_outputs
            )

            await api_channels.send_simulation_inputs(api_to_sim_inputs)

            await _wait_until(
                lambda: simulation_channels.get_simulation_inputs() == api_to_sim_inputs
            )
        finally:
            simulation_task.cancel()
            api_task.cancel()


async def test_directives_channels_to_directives_api_channels_roundtrip_all_channels(
    settings,
):
    test_id = uuid4().hex[:8]
    controller_prefix = f"test_controller_topic/{test_id}"

    async with (
        MqttClient(settings.mqtt_host, settings.mqtt_port) as directives_client,
        MqttClient(settings.mqtt_host, settings.mqtt_port) as api_client,
    ):
        directives_connector = MqttConnector(directives_client)
        api_connector = MqttConnector(api_client)

        directives_channels, directives_run = await directives_connector.run(
            DirectivesChannels,
            DirectivesChannelsDescription(controller_topic_prefix=controller_prefix),
        )
        directives_task = create_task(directives_run)

        api_channels, api_run = await api_connector.run(
            DirectivesApiChannels,
            DirectivesApiChannelsDescription(controller_topic_prefix=controller_prefix),
        )
        api_task = create_task(api_run)

        try:
            received: dict[str, object] = {}

            directives_channels.on_play(
                lambda msg: received.update(playback_rate=msg.playback_rate)
            )
            directives_channels.on_step(
                lambda msg: received.update(seconds=msg.seconds)
            )
            directives_channels.on_pause(lambda _msg: received.update(paused=True))

            await api_channels.send_play(1.25)
            await api_channels.send_step(2.5)
            await api_channels.send_pause()

            await _wait_until(
                lambda: received.get("playback_rate") == 1.25
                and received.get("seconds") == 2.5
                and received.get("paused") is True
            )

            status = SimulationStatusMessage(
                mode="thrusters",
                status="available",
                control_modules=["thrusters"],
                simulation_time=datetime.fromtimestamp(0),
            )
            await directives_channels.send_simulation_status(status)

            await _wait_until(lambda: api_channels.get_simulation_status() == status)
        finally:
            directives_task.cancel()
            api_task.cancel()
