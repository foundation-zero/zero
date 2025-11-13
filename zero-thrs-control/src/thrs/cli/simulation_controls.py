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

from thrs.classes.control import Control
from thrs.control.manual import ManualControl
from thrs.control.modules.consumers import ConsumersControl, ConsumersParameters
from thrs.control.modules.pcm import PcmAlarms, PcmControl, PcmParameters
from thrs.control.modules.pvt import PvtAlarms, PvtControl, PvtParameters
from thrs.control.modules.thrusters import (
    ThrustersAlarms,
    ThrustersControl,
    ThrustersParameters,
)
from thrs.control.switching import SwitchingControl
from thrs.input_output.base import (
    SimulationInputs,
    SimulationValues,
    Stamped,
    ThrsModel,
)
from thrs.input_output.definitions.simulation import (
    Boundary,
    FmuBoundary,
    HeatSource,
    Pcs,
    TemperatureBoundary,
    Thruster,
)
from thrs.input_output.definitions.units import PcsMode
from thrs.input_output.modules.consumers import ConsumersSimulationInputs
from thrs.input_output.modules.pcm import (
    PcmControlValues,
    PcmSensorValues,
    PcmSimulationInputs,
    PcmSimulationOutputs,
)
from thrs.input_output.modules.pvt import (
    PvtControlValues,
    PvtSensorValues,
    PvtSimulationInputs,
    PvtSimulationOutputs,
)
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
from thrs.orchestration.config import Config
from thrs.orchestration.executor import MqttExecutor, SimulationExecutor
from thrs.simulation.models.fmu_paths import (
    thrusters_path,
    pvt_path,
    pcm_path,
)
from thrs.orchestration.simulator import Simulator, SimulatorModel

logger = logging.getLogger(__name__)

INPUTS = {
    "thrusters": ThrustersSimulationInputs(
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
    ),
    "pvt": PvtSimulationInputs(
        pvt_main_fwd=HeatSource(heat_flow=Stamped.stamp(0)),
        pvt_main_aft=HeatSource(heat_flow=Stamped.stamp(0)),
        pvt_owners=HeatSource(heat_flow=Stamped.stamp(0)),
        pvt_module_supply=TemperatureBoundary(temperature=Stamped.stamp(50)),
        pvt_seawater_supply=Boundary(
            temperature=Stamped.stamp(32), flow=Stamped.stamp(50)
        ),
    ),
    "pcm": PcmSimulationInputs(
        pcm_producers_supply=Boundary(
            temperature=Stamped.stamp(70), flow=Stamped.stamp(80)
        ),
        pcm_consumers_supply=TemperatureBoundary(temperature=Stamped.stamp(30)),
        pcm_freshwater_supply=Boundary(
            temperature=Stamped.stamp(40), flow=Stamped.stamp(0)
        ),
    ),
    "consumers": ConsumersSimulationInputs(
        consumers_boosting_supply=FmuBoundary(
            temperature=Stamped.stamp(30.0),
            flow=Stamped.stamp(10.0),
            over_pressure=Stamped.stamp(0.2),
        ),
        consumers_fahrenheit_supply=FmuBoundary(
            temperature=Stamped.stamp(30.0),
            flow=Stamped.stamp(10.0),
            over_pressure=Stamped.stamp(0.2),
        ),
        consumers_module_supply=Boundary(
            temperature=Stamped.stamp(60.0), flow=Stamped.stamp(10.0)
        ),
    ),
}

CONTROL_PARAMS = {
    "thrusters": ThrustersParameters(),
    "pvt": PvtParameters(),
    "pcm": PcmParameters(),
    "consumers": ConsumersParameters(),
}

CONTROLS = {
    "thrusters": ThrustersControl,
    "pvt": PvtControl,
    "pcm": PcmControl,
    "consumers": ConsumersControl,
}

MODES = {
    "thrusters": SimulatorModel(
        fmu_path=thrusters_path,
        sensor_values_cls=ThrustersSensorValues,
        control_values_cls=ThrustersControlValues,
        simulation_outputs_cls=ThrustersSimulationOutputs,
        simulation_inputs=INPUTS["thrusters"],
        control_cls=CONTROLS["thrusters"],
        control_parameters=CONTROL_PARAMS["thrusters"],
        alarms=ThrustersAlarms(),
        tick_duration=timedelta(seconds=1),
        start_time=datetime.now(),
    ),
    "pvt": SimulatorModel(
        fmu_path=pvt_path,
        sensor_values_cls=PvtSensorValues,
        control_values_cls=PvtControlValues,
        simulation_outputs_cls=PvtSimulationOutputs,
        simulation_inputs=INPUTS["pvt"],
        control_cls=CONTROLS["pvt"],
        control_parameters=CONTROL_PARAMS["pvt"],
        alarms=PvtAlarms(),
        tick_duration=timedelta(seconds=1),
        start_time=datetime.now(),
    ),
    "pcm": SimulatorModel(
        fmu_path=pcm_path,
        sensor_values_cls=PcmSensorValues,
        control_values_cls=PcmControlValues,
        simulation_outputs_cls=PcmSimulationOutputs,
        simulation_inputs=INPUTS["pcm"],
        control_cls=CONTROLS["pcm"],
        control_parameters=CONTROL_PARAMS["pcm"],
        alarms=PcmAlarms(),
        tick_duration=timedelta(seconds=1),
        start_time=datetime.now(),
    ),
}

Modes = Literal["thrusters", "pvt", "pcm", "consumers"]


@dataclass
class MessageContext[
    SensorValues: ThrsModel,
    ControlValues: ThrsModel,
    Parameters: ThrsModel,
    Inputs: SimulationInputs,
    Outputs: SimulationValues,
]:
    cmds: "Queue[SimulationCtrlMessage]"
    switching_control: SwitchingControl[SensorValues, ControlValues, Parameters]
    manual_control: ManualControl[SensorValues, ControlValues]
    automatic_control: Control[SensorValues, ControlValues, Parameters]
    client: MqttClient
    executor: SimulationExecutor[
        SensorValues,
        ControlValues,
        Inputs,
        Outputs,
    ]


class IncomingMessage(ThrsModel):
    @staticmethod
    @abstractmethod
    def resolve[
        SensorValues: ThrsModel,
        ControlValues: ThrsModel,
        Parameters: ThrsModel,
        Inputs: SimulationInputs,
        Outputs: SimulationValues,
    ](
        sensor_values: type[SensorValues],
        control_values: type[ControlValues],
        parameters: type[Parameters],
        simulation_inputs: type[Inputs],
        simulation_outputs: type[Outputs],
    ) -> "type[IncomingMessage]": ...

    @staticmethod
    @abstractmethod
    def topic() -> str: ...

    @abstractmethod
    async def handle(self, context: MessageContext): ...


class OutgoingMessage(ThrsModel):
    @staticmethod
    @abstractmethod
    def topic() -> str: ...

    @staticmethod
    @abstractmethod
    def retained() -> bool: ...

    async def send(self, client: MqttClient):
        return await client.publish(
            self.topic(),
            self.model_dump_json(),
            qos=1,
            retain=self.retained(),
        )


class SimulationStatusMessage(OutgoingMessage):
    status: Literal["available", "running", "stepping"]
    module: Modes
    simulation_time: datetime

    @staticmethod
    def topic() -> str:
        return "thrs/simulation/status"

    @staticmethod
    def retained() -> bool:
        return True


class ControlStatusMessage(OutgoingMessage):
    automatic: bool

    @staticmethod
    def topic() -> str:
        return "thrs/controls/status"

    @staticmethod
    def retained() -> bool:
        return True


class ParametersMessage[Parameters: ThrsModel](OutgoingMessage):
    parameters: Parameters

    @staticmethod
    def topic() -> str:
        return "thrs/parameters"

    @staticmethod
    def retained() -> bool:
        return True


class SimulationInputMessage[Inputs: ThrsModel](OutgoingMessage):
    inputs: Inputs

    @staticmethod
    def topic() -> str:
        return "thrs/simulation/inputs"

    @staticmethod
    def retained() -> bool:
        return True


class SimulationCtrlMessage(IncomingMessage):
    async def handle(self, context: MessageContext):
        await context.cmds.put(self)


class PlayMessage(SimulationCtrlMessage):
    playback_rate: Annotated[float, Field(ge=0.25, le=10)] = 1.0

    @staticmethod
    def resolve[
        SensorValues: ThrsModel,
        ControlValues: ThrsModel,
        Parameters: ThrsModel,
        Inputs: SimulationInputs,
        Outputs: SimulationValues,
    ](
        sensor_values: type[SensorValues],
        control_values: type[ControlValues],
        parameters: type[Parameters],
        simulation_inputs: type[Inputs],
        simulation_outputs: type[Outputs],
    ) -> "type[IncomingMessage]":
        return PlayMessage

    @staticmethod
    def topic() -> str:
        return "thrs/simulation/play"


class StepMessage(SimulationCtrlMessage):
    seconds: Annotated[float, Field(ge=0)]

    @staticmethod
    def resolve[
        SensorValues: ThrsModel,
        ControlValues: ThrsModel,
        Parameters: ThrsModel,
        Inputs: SimulationInputs,
        Outputs: SimulationValues,
    ](
        sensor_values: type[SensorValues],
        control_values: type[ControlValues],
        parameters: type[Parameters],
        simulation_inputs: type[Inputs],
        simulation_outputs: type[Outputs],
    ) -> "type[IncomingMessage]":
        return StepMessage

    @staticmethod
    def topic() -> str:
        return "thrs/simulation/step"


class PauseMessage(SimulationCtrlMessage):
    @staticmethod
    def resolve[
        SensorValues: ThrsModel,
        ControlValues: ThrsModel,
        Parameters: ThrsModel,
        Inputs: SimulationInputs,
        Outputs: SimulationValues,
    ](
        sensor_values: type[SensorValues],
        control_values: type[ControlValues],
        parameters: type[Parameters],
        simulation_inputs: type[Inputs],
        simulation_outputs: type[Outputs],
    ) -> "type[IncomingMessage]":
        return PauseMessage

    @staticmethod
    def topic() -> str:
        return "thrs/simulation/pause"


class ManualControlMessage[ControlValues: ThrsModel](IncomingMessage):
    control_values: ControlValues

    @staticmethod
    def resolve[
        SensorValues: ThrsModel,
        LControlValues: ThrsModel,
        Parameters: ThrsModel,
        Inputs: SimulationInputs,
        Outputs: SimulationValues,
    ](
        sensor_values: type[SensorValues],
        control_values: type[LControlValues],
        parameters: type[Parameters],
        simulation_inputs: type[Inputs],
        simulation_outputs: type[Outputs],
    ) -> "type[IncomingMessage]":
        return ManualControlMessage[control_values]

    @staticmethod
    def topic() -> str:
        return "thrs/controls/manual"

    async def handle(
        self,
        context: MessageContext[
            ThrsModel, ControlValues, ThrsModel, SimulationInputs, SimulationValues
        ],
    ):
        context.manual_control.manual_controls(self.control_values)


class SetAutomationMessage(IncomingMessage):
    enabled: bool

    @staticmethod
    def resolve[
        SensorValues: ThrsModel,
        ControlValues: ThrsModel,
        Parameters: ThrsModel,
        Inputs: SimulationInputs,
        Outputs: SimulationValues,
    ](
        sensor_values: type[SensorValues],
        control_values: type[ControlValues],
        parameters: type[Parameters],
        simulation_inputs: type[Inputs],
        simulation_outputs: type[Outputs],
    ) -> "type[IncomingMessage]":
        return SetAutomationMessage

    @staticmethod
    def topic() -> str:
        return "thrs/controls/set_automation"

    async def handle(self, context: MessageContext):
        context.switching_control.switch_mode("automatic" if self.enabled else "manual")
        await ControlStatusMessage(automatic=self.enabled).send(context.client)


class SetParametersMessage[Parameters: ThrsModel](IncomingMessage):
    parameters: Parameters

    @staticmethod
    def resolve[
        SensorValues: ThrsModel,
        ControlValues: ThrsModel,
        LParameters: ThrsModel,
        Inputs: SimulationInputs,
        Outputs: SimulationValues,
    ](
        sensor_values: type[SensorValues],
        control_values: type[ControlValues],
        parameters: type[LParameters],
        simulation_inputs: type[Inputs],
        simulation_outputs: type[Outputs],
    ) -> "type[IncomingMessage]":
        return SetParametersMessage[parameters]

    @staticmethod
    def topic() -> str:
        return "thrs/controls/set_parameters"

    async def handle(self, context: MessageContext[Any, Any, Parameters, Any, Any]):
        context.automatic_control.update_parameters(self.parameters)
        await ParametersMessage[Parameters](
            parameters=context.automatic_control.parameters
        ).send(context.client)


class SetSimulationInputsMessage[Inputs: SimulationInputs](IncomingMessage):
    inputs: Inputs

    @staticmethod
    def resolve[
        SensorValues: ThrsModel,
        ControlValues: ThrsModel,
        Parameters: ThrsModel,
        LInputs: SimulationInputs,
        Outputs: SimulationValues,
    ](
        sensor_values: type[SensorValues],
        control_values: type[ControlValues],
        parameters: type[Parameters],
        simulation_inputs: type[LInputs],
        simulation_outputs: type[Outputs],
    ) -> "type[IncomingMessage]":
        return SetSimulationInputsMessage[simulation_inputs]

    @staticmethod
    def topic() -> str:
        return "thrs/simulation/set_inputs"

    async def handle(self, context: MessageContext):
        context.executor.update_simulation_inputs(self.inputs)
        await SimulationInputMessage(inputs=self.inputs).send(context.client)


HANDLERS = [
    PlayMessage,
    StepMessage,
    PauseMessage,
    ManualControlMessage,
    SetAutomationMessage,
    SetParametersMessage,
    SetSimulationInputsMessage,
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
        self,
        handlers: list[IncomingMessage],
        cmds: Queue[SimulationCtrlMessage],
        switching_control: SwitchingControl,
        automatic_control: Control,
        manual_control: ManualControl,
        executor: SimulationExecutor,
    ):
        context = MessageContext(
            cmds,
            switching_control,
            manual_control,
            automatic_control,
            self._controls_client,
            executor,
        )
        async for message in self._controls_client.messages:
            for handler in handlers:
                if message.topic.matches(handler.topic()) and isinstance(
                    message.payload, str | bytes
                ):
                    logger.debug(
                        f"Received message on topic {message.topic}, handling {handler}"
                    )
                    await handler.model_validate_json(message.payload).handle(context)
                    break

    async def clear_previous(self):
        for msg in [
            SimulationStatusMessage,
            ControlStatusMessage,
            ParametersMessage,
            SimulationInputMessage,
        ]:
            if msg.retained():
                await self._controls_client.publish(
                    msg.topic(), None, qos=1, retain=True
                )  # Clear previous messages

    async def run(self, mode: Modes):
        for handler in HANDLERS:
            await self._controls_client.subscribe(handler.topic(), qos=1)

        model = MODES[mode]

        resolved_handlers = [
            handler.resolve(
                model.sensor_values_cls,
                model.control_values_cls,
                type(model.control_parameters),
                type(model.simulation_inputs),
                model.simulation_outputs_cls,
            )
            for handler in HANDLERS
        ]

        switching_control_model = replace(model, control_cls=SwitchingControl)
        with switching_control_model.executor() as inner_executor:
            manual_control = ManualControl(
                model.control_values_cls.zero(), inner_executor.time
            )
            automated_control = model.control_cls(
                model.control_parameters, inner_executor.time
            )
            await ControlStatusMessage(automatic=False).send(self._controls_client)
            switching_control = SwitchingControl(manual_control, automated_control)
            executor = MqttExecutor(
                inner_executor,
                self._control_client,
                self._sensor_client,
                self._sensor_topic,
                model.sensor_values_cls,
                self._control_topic,
                model.control_values_cls,
            )
            simulator = Simulator(switching_control_model, executor, switching_control)
            cmds: Queue[SimulationCtrlMessage] = Queue()

            await executor.start()
            executor_task = create_task(executor.run())
            receive_task = create_task(
                self._receive_controls(
                    resolved_handlers,
                    cmds,
                    switching_control,
                    automated_control,
                    manual_control,
                    inner_executor,
                )
            )
            try:
                await ParametersMessage(parameters=automated_control.parameters).send(
                    self._controls_client
                )
                await SimulationInputMessage(
                    inputs=cast(ThrustersSimulationInputs, model.simulation_inputs)
                ).send(self._controls_client)
                await self._run_simulation(mode, model, executor, simulator, cmds)
            finally:
                executor_task.cancel()
                receive_task.cancel()

    async def _run_simulation(
        self,
        module: Modes,
        model: SimulatorModel,
        executor: MqttExecutor,
        simulator: Simulator,
        cmds: Queue[SimulationCtrlMessage],
    ):
        logging.debug("Simulation control loop started")
        while True:
            await SimulationStatusMessage(
                status="available",
                simulation_time=executor.time(),
                module=module,
            ).send(self._controls_client)
            cmd = await cmds.get()
            if isinstance(cmd, PlayMessage):
                sleep_duration = model.tick_duration.total_seconds() / cmd.playback_rate
                await SimulationStatusMessage(
                    status="running",
                    simulation_time=executor.time(),
                    module=module,
                ).send(self._controls_client)
                logging.debug(
                    f"Starting simulation with tick interval of {sleep_duration} seconds"
                )
                while cmds.empty():
                    async with TaskGroup() as tg:
                        tg.create_task(sleep(sleep_duration))
                        tg.create_task(simulator.run(1))
                logger.debug("Simulation paused")
            elif isinstance(cmd, StepMessage):
                await SimulationStatusMessage(
                    status="stepping",
                    simulation_time=executor.time(),
                    module=module,
                ).send(self._controls_client)

                ticks = max(1, int(cmd.seconds / model.tick_duration.total_seconds()))
                logging.debug(f"Stepping simulation by {ticks} ticks")
                await simulator.run(ticks)
