from abc import abstractmethod
from asyncio import Queue, TaskGroup, create_task, sleep
from contextlib import asynccontextmanager
from dataclasses import dataclass, replace
from datetime import datetime, timedelta
import logging
from typing import (
    Annotated,
    Any,
    Literal,
    cast,
)
from aiomqtt import Client as MqttClient
from pydantic import Field

from thrs.control.manual import ManualControl
from thrs.control.modules.thrusters import (
    ThrustersAlarms,
    ThrustersControl,
    ThrustersParameters,
)
from thrs.control.switching import SwitchingControl
from thrs.input_output.base import Stamped, ThrsModel
from thrs.input_output.definitions.simulation import (
    Boundary,
    Pcs,
    TemperatureBoundary,
    Thruster,
)
from thrs.input_output.definitions.units import PcsMode
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
from thrs.orchestration.config import Config
from thrs.orchestration.executor import MqttExecutor
from thrs.simulation.models.fmu_paths import thrusters_path
from thrs.orchestration.simulator import Simulator, SimulatorModel

logger = logging.getLogger(__name__)

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
        thrusters_pcs=Pcs(mode=Stamped.stamp(PcsMode.PROPULSION)),
    )
}

CONTROL_PARAMS = {"THRUSTERS": ThrustersParameters()}

CONTROLS = {"THRUSTERS": ThrustersControl}

MODES = {
    "THRUSTERS": SimulatorModel(
        fmu_path=thrusters_path,
        sensor_values_cls=ThrustersSensorValues,
        control_values_cls=ThrustersControlValues,
        simulation_outputs_cls=ThrustersSimulationOutputs,
        simulation_inputs=INPUTS["THRUSTERS"],
        control_cls=CONTROLS["THRUSTERS"],
        control_parameters=CONTROL_PARAMS["THRUSTERS"],
        alarms=ThrustersAlarms(),
        tick_duration=timedelta(seconds=1),
        start_time=datetime.now(),
    )
}

Modes = Literal["THRUSTERS"]


@dataclass
class MessageContext:
    cmds: "Queue[SimulationCtrlMessage]"
    switching_control: SwitchingControl
    manual_control: ManualControl
    client: MqttClient


class IncomingMessage(ThrsModel):
    @staticmethod
    @abstractmethod
    def topic() -> str: ...

    @abstractmethod
    async def handle(self, context: MessageContext): ...


class OutgoingMessage(ThrsModel):
    @staticmethod
    @abstractmethod
    def topic() -> str: ...


class SimulationStatusMessage(OutgoingMessage):
    status: Literal["available", "running", "stepping"]
    simulation_time: datetime

    @staticmethod
    def topic() -> str:
        return "thrs/simulation/status"


class ControlStatusMessage(OutgoingMessage):
    automatic: bool

    @staticmethod
    def topic() -> str:
        return "thrs/controls/status"

    async def send(self, client: MqttClient):
        return client.publish(
            self.topic(),
            self.model_dump_json(),
            qos=1,
            retain=True,
        )


class SimulationCtrlMessage(IncomingMessage):
    async def handle(self, context: MessageContext):
        await context.cmds.put(self)


class PlayMessage(SimulationCtrlMessage):
    playback_rate: Annotated[float, Field(ge=0.25, le=10)] = 1.0

    @staticmethod
    def topic() -> str:
        return "thrs/simulation/play"


class StepMessage(SimulationCtrlMessage):
    seconds: Annotated[float, Field(ge=0)]

    @staticmethod
    def topic() -> str:
        return "thrs/simulation/step"


class PauseMessage(SimulationCtrlMessage):
    @staticmethod
    def topic() -> str:
        return "thrs/simulation/pause"


class ManualControlMessage(ThrsModel):
    control_values: ThrustersControlValues

    @staticmethod
    def topic() -> str:
        return "thrs/controls/manual"

    async def handle(self, context: MessageContext):
        context.manual_control.manual_controls(self.control_values)


class SetAutomationMessage(ThrsModel):
    enabled: bool

    @staticmethod
    def topic() -> str:
        return "thrs/controls/set_automation"

    async def handle(self, context: MessageContext):
        context.switching_control.switch_mode("automatic" if self.enabled else "manual")
        await ControlStatusMessage(automatic=self.enabled).send(context.client)


HANDLERS = [
    PlayMessage,
    StepMessage,
    PauseMessage,
    ManualControlMessage,
    SetAutomationMessage,
]


class SimulationControls:
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
        self._controls_client = controls_client
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

    async def _receive_controls(
        self, cmds, switching_control: SwitchingControl, manual_control: ManualControl
    ):
        context = MessageContext(
            cmds, switching_control, manual_control, self._controls_client
        )
        async for message in self._controls_client.messages:
            for handler in HANDLERS:
                if message.topic.matches(handler.topic()) and isinstance(
                    message.payload, str | bytes
                ):
                    logger.debug(
                        f"Received message on topic {message.topic}, handling {handler}"
                    )
                    await handler.model_validate_json(message.payload).handle(context)
                    break

    async def run(self, mode: Modes):
        for handler in HANDLERS:
            await self._controls_client.subscribe(handler.topic(), qos=1)

        model = MODES[mode]
        switching_control_model = replace(model, control_cls=SwitchingControl)
        with switching_control_model.executor() as executor:
            manual_control = ManualControl(ThrustersControlValues.zero(), executor.time)
            automated_control = ThrustersControl(
                cast(ThrustersParameters, model.control_parameters), executor.time
            )
            automated_control.to_idle(ThrustersSensorValues.zero())  # type: ignore
            await ControlStatusMessage(automatic=False).send(self._controls_client)
            switching_control = SwitchingControl(manual_control, automated_control)
            executor = MqttExecutor(
                executor,
                self._control_client,
                self._sensor_client,
                self._sensor_topic,
                ThrustersSensorValues,
                self._control_topic,
                ThrustersControlValues,
            )
            simulator = Simulator(switching_control_model, executor, switching_control)
            cmds: Queue[SimulationCtrlMessage] = Queue()

            await executor.start()
            executor_task = create_task(executor.run())
            receive_task = create_task(
                self._receive_controls(cmds, switching_control, manual_control)
            )
            try:
                await self._run_simulation(model, executor, simulator, cmds)
            finally:
                executor_task.cancel()
                receive_task.cancel()

    async def _run_simulation(
        self,
        model: SimulatorModel,
        executor: MqttExecutor[ThrustersSensorValues, ThrustersControlValues],
        simulator: Simulator,
        cmds: Queue[SimulationCtrlMessage],
    ):
        while True:
            await self._send_simulation_status(
                SimulationStatusMessage(
                    status="available",
                    simulation_time=executor.time(),
                )
            )
            cmd = await cmds.get()
            if isinstance(cmd, PlayMessage):
                sleep_duration = model.tick_duration.total_seconds() / cmd.playback_rate
                await self._send_simulation_status(
                    SimulationStatusMessage(
                        status="running",
                        simulation_time=executor.time(),
                    )
                )
                logging.debug(
                    f"Starting simulation with tick interval of {sleep_duration} seconds"
                )
                while cmds.empty():
                    async with TaskGroup() as tg:
                        tg.create_task(sleep(sleep_duration))
                        tg.create_task(simulator.run(1))
                logger.debug("Simulation paused")
            elif isinstance(cmd, StepMessage):
                await self._send_simulation_status(
                    SimulationStatusMessage(
                        status="stepping",
                        simulation_time=executor.time(),
                    )
                )

                ticks = max(1, int(cmd.seconds / model.tick_duration.total_seconds()))
                logging.debug(f"Stepping simulation by {ticks} ticks")
                await simulator.run(ticks)

    async def _send_simulation_status(self, msg: SimulationStatusMessage):
        await self._controls_client.publish(
            "thrs/simulation/status",
            msg.model_dump_json(),
            qos=1,
            retain=True,
        )


def update_in_place(model, values: dict[str, Any]):
    """Update a model in place with values from a dictionary."""
    for key, value in values.items():
        if hasattr(model, key) and isinstance(getattr(model, key), type(value)):
            setattr(model, key, value)
        elif hasattr(model, key) and isinstance(value, dict):
            setattr(model, key, getattr(model, key).model_validate(value))
        else:
            raise ValueError(f"Key {key} not found in model {model.__class__.__name__}")
