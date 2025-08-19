from asyncio import create_task
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Annotated, Any, Awaitable, ClassVar, Literal, overload
from aiomqtt import Client as MqttClient
from pydantic import BaseModel, Field, TypeAdapter, ValidationError
from pydantic_partial import create_partial_model

from control.modules.thrusters import (
    ThrustersAlarms,
    ThrustersControl,
    ThrustersParameters,
)
from input_output.base import Stamped, ThrsModel
from input_output.definitions.simulation import (
    Boundary,
    Pcs,
    TemperatureBoundary,
    Thruster,
)
from input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
from orchestration.config import Config
from orchestration.executor import MqttExecutor
from simulation.models.fmu_paths import thrusters_path
from orchestration.simulator import Simulator, SimulatorModel


INPUTS = {
    "THRUSTERS": ThrustersSimulationInputs(
        thrusters_aft=Thruster(
            heat_flow=Stamped.stamp(9000.0), active=Stamped.stamp(True)
        ),
        thrusters_fwd=Thruster(
            heat_flow=Stamped.stamp(4300.0), active=Stamped.stamp(True)
        ),
        thrusters_seawater_supply=Boundary(
            temperature=Stamped.stamp(32.0), flow=Stamped.stamp(64.0)
        ),
        thrusters_module_supply=TemperatureBoundary(temperature=Stamped.stamp(40.0)),
        thrusters_pcs=Pcs(mode=Stamped.stamp("propulsion")),
    )
}

CONTROL_PARAMS = {"THRUSTERS": ThrustersParameters()}

CONTROLS = {"THRUSTERS": ThrustersControl(CONTROL_PARAMS["THRUSTERS"])}

MODES = {
    "THRUSTERS": SimulatorModel(
        fmu_path=thrusters_path,
        sensor_values_cls=ThrustersSensorValues,
        control_values_cls=ThrustersControlValues,
        simulation_outputs_cls=ThrustersSimulationOutputs,
        simulation_inputs=INPUTS["THRUSTERS"],
        control=CONTROLS["THRUSTERS"],
        alarms=ThrustersAlarms(),
        tick_duration=timedelta(seconds=1),
        start_time=datetime.now(),
    )
}

async def test() -> int:
    return 5

class StatusMessage(ThrsModel):
    """Sent message to indicate simulation status"""

    TOPIC: ClassVar[str] = "thrs/simulation/status"
    status: Literal[
        "available",
        "mode_picking",
        "value_setting",
        "ready_to_start",
        "ready_to_run",
        "running",
        "ran",
    ]


class ConnectMessage(ThrsModel):
    """Received message to connect to the simulation"""

    TOPIC: ClassVar[str] = "thrs/simulation/connect"


type Modes = Literal["THRUSTERS"]


class AllowedModesMessage(ThrsModel):
    """Sent message to return allowed modes for the simulation"""

    TOPIC: ClassVar[str] = "thrs/simulation/allowed_modes"
    modes: list[Modes]


class PickModeMessage(ThrsModel):
    """Received message to pick a mode for the simulation"""

    TOPIC: ClassVar[str] = "thrs/simulation/mode"
    mode: Modes


class SchemaMessage[T: ThrsModel](ThrsModel):
    """Sent message to return the JSON schema of sensors, controls, simulation inputs and parameters and the simulation inputs values"""

    TOPIC: ClassVar[str] = "thrs/simulation/schemas"
    sensors: dict[str, Any]
    controls: dict[str, Any]
    simulation_inputs: dict[str, Any]
    simulation_inputs_values: T  # Ideally this would be placed in the simulation inputs schema, but that means dynamically recursively rebuilding the pydantic models to specify the default from the instance
    control_params: dict[str, Any]
    control_modes: dict[str, Any]


class SetValuesMessage[SI: ThrsModel, P: ThrsModel](ThrsModel):
    """Received message to set values for simulation inputs and control parameters"""

    TOPIC: ClassVar[str] = "thrs/simulation/set_values"
    simulation_inputs: SI
    control_params: P
    control_mode: str


class StartCommandMessage(ThrsModel):
    """Received message to start the simulation with a specified start time and number of ticks"""

    TOPIC: ClassVar[str] = "thrs/simulation/start"
    ticks: int
    start_time: datetime


class RunCommandMessage(ThrsModel):
    """Received message to run the simulation for a specified number of ticks"""

    TOPIC: ClassVar[str] = "thrs/simulation/run"
    ticks: int


def schemas_for_mode(mode: Modes) -> SchemaMessage:
    return SchemaMessage(
        sensors=MODES[mode].sensor_values_cls.model_json_schema(),
        controls=MODES[mode].control_values_cls.model_json_schema(),
        simulation_inputs=INPUTS[mode].model_json_schema(),
        simulation_inputs_values=INPUTS[mode],
        control_params=MODES[mode].control.parameters.model_json_schema(),
        control_modes=TypeAdapter(
            Annotated[
                Literal[*CONTROLS[mode].modes],
                Field(default=CONTROLS[mode].mode),
            ]
        ).json_schema(),
    )


class SimulationControls:
    """Handling of simulation controls from front end

    Message sequence:
    -> Status available
    <- Connect
    -> Return allowed modes
    <- Pick mode
    -> Send json schema of sensors, controls, simulation inputs and parameters
    <- Receive simulation inputs and parameters
    -> Status ready_to_start
    <- Receive start command (start time and number of ticks to run)
    -> Status running
    -> Status ran and send sensor values, control values and simulation outputs

    <- Receive set values (simulation inputs and control parameters)
    -> Status ready_to_run
    <- Receive run command (number of ticks to run)
    -> Status running
    -> Status ran and send sensor values, control values and simulation outputs
    (repeat)
    """

    def __init__(
        self,
        controls_client: MqttClient,
        control_client: MqttClient,
        sensor_client: MqttClient,
        sensor_topic: str,
        control_topic: str,
    ):
        self._sensor_client = sensor_client
        self._control_client = control_client
        self._sequencer = MqttSequencer(controls_client)
        self._sensor_topic = sensor_topic
        self._control_topic = control_topic

    @staticmethod
    @asynccontextmanager
    async def from_settings(settings: Config):
        async with (
            MqttClient(settings.mqtt_host, settings.mqtt_port) as controls_client,
            MqttClient(settings.mqtt_host, settings.mqtt_port) as control_client,
            MqttClient(settings.mqtt_host, settings.mqtt_port) as sensor_client,
        ):
            yield SimulationControls(
                controls_client=controls_client,
                control_client=control_client,
                sensor_client=sensor_client,
                sensor_topic=settings.mqtt_sensor_topic,
                control_topic=settings.mqtt_control_topic,
            )

    def _apply_values(self, model: SimulatorModel, values: Any):
        if values.simulation_inputs:
            update_in_place(
                model.simulation_inputs,
                values.simulation_inputs.model_dump(exclude_none=True),
            )
        if values.control_params:
            update_in_place(
                model.control.parameters,
                values.control_params.model_dump(exclude_none=True),
            )
        if values.control_mode:
            getattr(model.control, f"to_{values.control_mode}")()  # type: ignore

    async def run(self):
        await self._sequencer.reset_on("thrs/simulation/reset")
        while True:
            try:
                await_connection = await self._sequencer.expect(
                    ConnectMessage.TOPIC, ConnectMessage
                )
                await self._sequencer.reply(
                    StatusMessage.TOPIC, StatusMessage(status="available")
                )
                await await_connection

                await_pick_mode = await self._sequencer.expect(
                    PickModeMessage.TOPIC, PickModeMessage
                )

                await self._sequencer.reply(
                    StatusMessage.TOPIC, StatusMessage(status="mode_picking")
                )
                await self._sequencer.reply(
                    AllowedModesMessage.TOPIC,
                    AllowedModesMessage(modes=["THRUSTERS"]),
                )

                picked_mode = await await_pick_mode
                model = MODES[picked_mode.mode]

                class SetValuesMessageWithModel(
                    SetValuesMessage[
                        create_partial_model(model.simulation_inputs.__class__),
                        create_partial_model(model.control.parameters.__class__),
                    ]
                ):
                    pass

                PartialSetValuesMessage = create_partial_model(
                    SetValuesMessageWithModel
                )

                await self._sequencer.reply(
                    StatusMessage.TOPIC, StatusMessage(status="value_setting")
                )
                await_set_values = await self._sequencer.expect(
                    SetValuesMessageWithModel.TOPIC, PartialSetValuesMessage
                )

                await self._sequencer.reply(
                    SchemaMessage.TOPIC,
                    SchemaMessage(
                        sensors=model.sensor_values_cls.model_json_schema(),
                        controls=model.control_values_cls.model_json_schema(),
                        simulation_inputs=model.simulation_inputs.model_json_schema(),
                        simulation_inputs_values=model.simulation_inputs,
                        control_params=model.control.parameters.model_json_schema(),
                        control_modes=TypeAdapter(
                            Annotated[
                                Literal[*model.control.modes],
                                Field(default=model.control.mode),
                            ]
                        ).json_schema(),
                    ),
                )

                values = await await_set_values
                self._apply_values(model, values)

                await_start = await self._sequencer.expect(
                    StartCommandMessage.TOPIC, StartCommandMessage
                )

                await self._sequencer.reply(
                    StatusMessage.TOPIC,
                    StatusMessage(status="ready_to_start"),
                )

                start_settings = await await_start

                with model.executor() as executor:
                    executor = MqttExecutor(
                        executor,
                        self._control_client,
                        self._sensor_client,
                        self._sensor_topic,
                        ThrustersSensorValues,
                        self._control_topic,
                        ThrustersControlValues,
                    )
                    model.start_time = start_settings.start_time
                    simulator = Simulator(model, executor)
                    await executor.start()
                    create_task(executor.run())

                    await self._sequencer.reply(
                        StatusMessage.TOPIC,
                        StatusMessage(status="running"),
                    )

                    await simulator.run(start_settings.ticks)

                    while True:
                        await_set_values = await self._sequencer.expect(
                            SetValuesMessage.TOPIC, PartialSetValuesMessage
                        )
                        await self._sequencer.reply(
                            StatusMessage.TOPIC,
                            StatusMessage(status="ran"),
                        )
                        values = await await_set_values
                        self._apply_values(model, values)

                        await_run = await self._sequencer.expect(
                            RunCommandMessage.TOPIC, RunCommandMessage
                        )
                        await self._sequencer.reply(
                            StatusMessage.TOPIC,
                            StatusMessage(status="ready_to_run"),
                        )
                        run = await await_run

                        await self._sequencer.reply(
                            StatusMessage.TOPIC,
                            StatusMessage(status="running"),
                        )
                        await simulator.run(run.ticks)

            except ResetError:
                pass  # Reset the sequencer and start over


def update_in_place(model, values: dict[str, Any]):
    """Update a model in place with values from a dictionary."""
    for key, value in values.items():
        if hasattr(model, key) and isinstance(getattr(model, key), type(value)):
            setattr(model, key, value)
        elif hasattr(model, key) and isinstance(value, dict):
            setattr(model, key, getattr(model, key).model_validate(value))
        else:
            raise ValueError(f"Key {key} not found in model {model.__class__.__name__}")


class ResetError(Exception):
    """Exception raised to reset the sequencer when a reset message is received."""

    pass


class MqttSequencer:
    def __init__(self, mqtt_client: MqttClient) -> None:
        self._mqtt_client = mqtt_client
        self._reset_topic: str | None = None

    async def reset_on(self, topic: str) -> None:
        """Set up the sequencer to reset on a specific topic.

        If a message is received on this topic, the sequencer will reset by raising an ResetError on expect.
        """
        if self._reset_topic is not None:
            await self._mqtt_client.unsubscribe(self._reset_topic)
        self._reset_topic = topic
        await self._mqtt_client.subscribe(topic, qos=1)

    @overload
    async def expect[T: BaseModel](
        self, topic: str, message_cls: type[T], count: Literal[1] = 1
    ) -> Awaitable[T]:
        """Subscribe to a topic and wait for a single message of the specified type."""
        ...

    @overload
    async def expect[T: BaseModel](
        self, topic: str, message_cls: type[T], count: int
    ) -> Awaitable[list[T]]:
        """Subscribe to a topic and wait for multiple messages of the specified type."""
        ...

    async def expect[T: BaseModel](
        self, topic: str, message_cls: type[T], count: int = 1
    ) -> Awaitable[T | list[T]]:
        """Subscribe to a topic and wait for a message of the specified type.

        The returned awaitable signals the readiness for receiving the expected message.
        The awaitable within the awaitable actually waits for the message and returns it.
        ```python
        expectation = await mqtt_sequencer.expect(
            "some/topic", SomeMessageType
        )
        # Now the sequencer is subscribed and ready to receive the expected message.
        # This might be a good place to signal to a client that it can send the message.
        message = await expectation
        # Now the actual message has been received and validated.
        ```
        """
        await self._mqtt_client.subscribe(topic, qos=2)

        async def _wait_for_message(topic: str, message_cls: type[T]) -> T | list[T]:
            collected: list[T] = []
            async for message in self._mqtt_client.messages:
                if self._reset_topic and message.topic.matches(self._reset_topic):
                    raise ResetError()
                elif message.topic.matches(topic):
                    try:
                        if isinstance(message.payload, str | bytes) and (
                            parsed := message_cls.model_validate_json(message.payload)
                        ):
                            collected.append(parsed)
                            if len(collected) == count:
                                await self._mqtt_client.unsubscribe(topic)
                                if count == 1:
                                    return parsed
                                else:
                                    return collected

                    except ValidationError:
                        pass  # Skip validation errors (maybe add logging in future)

            raise ValueError(f"No message received on topic {topic}")

        return _wait_for_message(topic, message_cls)

    async def reply(self, topic: str, message: BaseModel) -> None:
        await self._mqtt_client.publish(topic, message.model_dump_json(), qos=2)
