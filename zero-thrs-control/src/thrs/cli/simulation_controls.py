from abc import abstractmethod
from asyncio import Queue, TaskGroup, create_task, sleep
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from typing import (
    Annotated,
    Any,
    Generator,
    Literal,
    cast,
)
from aiomqtt import Client as MqttClient
from pydantic import (
    Field,
    ValidationInfo,
    model_validator,
)

from thrs.control.modules.high_temperature import HighTemperatureModule
from thrs.control.switching import SwitchingControlMode
from thrs.input_output.modules.high_temperature import HighTemperatureSimulationInputs
from thrs.orchestration.module import ModuleDescription, CombinedModule, CombinedControl
from thrs.control.modules.consumers import (
    ConsumersAlarms,
    ConsumersControl,
    ConsumersControlMode,
    ConsumersParameters,
)
from thrs.control.modules.pcm import (
    PcmAlarms,
    PcmControl,
    PcmControlMode,
    PcmParameters,
)
from thrs.control.modules.pvt import (
    PvtAlarms,
    PvtControl,
    PvtControlMode,
    PvtParameters,
)
from thrs.control.modules.thrusters import (
    ThrustersAlarms,
    ThrustersControl,
    ThrustersControlMode,
    ThrustersParameters,
)
from thrs.input_output.base import (
    CombinedValues,
    SimulationInputs,
    SimulationValues,
    Stamped,
    ThrsValues,
)
from thrs.input_output.definitions.simulation import (
    Boundary,
    ExchangerBoundary,
    HeatSource,
    Pcs,
    TemperatureBoundary,
    Thruster,
)
from thrs.input_output.definitions.units import PcsMode
from thrs.input_output.modules.consumers import (
    ConsumersControlValues,
    ConsumersSensorValues,
    ConsumersSimulationInputs,
    ConsumersSimulationOutputs,
)
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
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import (
    thrusters_path,
    pvt_path,
    pcm_path,
    consumers_path,
    high_temperature_path,
)
from thrs.orchestration.simulator import Simulator

logger = logging.getLogger(__name__)

settings = Config()  # type: ignore

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
        consumers_boosting_supply=ExchangerBoundary(
            temperature=Stamped.stamp(30.0),
            flow=Stamped.stamp(10.0),
            overpressure=Stamped.stamp(0.2),
        ),
        consumers_fahrenheit_supply=ExchangerBoundary(
            temperature=Stamped.stamp(30.0),
            flow=Stamped.stamp(10.0),
            overpressure=Stamped.stamp(0.2),
        ),
        consumers_module_supply=Boundary(
            temperature=Stamped.stamp(60.0), flow=Stamped.stamp(10.0)
        ),
    ),
    "high_temperature": HighTemperatureSimulationInputs(
        thrusters_aft=Thruster(
            heat_flow=Stamped.stamp(9000.0), active=Stamped.stamp(True)
        ),
        thrusters_fwd=Thruster(
            heat_flow=Stamped.stamp(0.0), active=Stamped.stamp(True)
        ),
        thrusters_seawater_supply=Boundary(
            temperature=Stamped.stamp(32.0),
            flow=Stamped.stamp(64.0),
        ),
        thrusters_pcs=Pcs(mode=Stamped.stamp(PcsMode.PROPULSION)),
        pvt_main_fwd=HeatSource(heat_flow=Stamped.stamp(0)),
        pvt_main_aft=HeatSource(heat_flow=Stamped.stamp(0)),
        pvt_owners=HeatSource(heat_flow=Stamped.stamp(0)),
        pvt_seawater_supply=Boundary(
            temperature=Stamped.stamp(32), flow=Stamped.stamp(50)
        ),
        pcm_freshwater_supply=Boundary(
            temperature=Stamped.stamp(40.0),
            flow=Stamped.stamp(0.0),
        ),
        consumers_fahrenheit_supply=ExchangerBoundary(
            temperature=Stamped.stamp(30.0),
            flow=Stamped.stamp(0.0),
            overpressure=Stamped.stamp(0.2),
        ),
        consumers_boosting_supply=ExchangerBoundary(
            temperature=Stamped.stamp(30.0),
            flow=Stamped.stamp(0.0),
            overpressure=Stamped.stamp(0.2),
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

THRUSTERS_MODULE_DESCRIPTION = ModuleDescription(
    ThrustersSensorValues,
    ThrustersControlValues,
    ThrustersParameters,
    ThrustersControl,
    ThrustersControlMode,
    ThrustersAlarms,
)

PVT_MODULE_DESCRIPTION = ModuleDescription(
    PvtSensorValues,
    PvtControlValues,
    PvtParameters,
    PvtControl,
    PvtControlMode,
    PvtAlarms,
)

PCM_MODULE_DESCRIPTION = ModuleDescription(
    PcmSensorValues,
    PcmControlValues,
    PcmParameters,
    PcmControl,
    PcmControlMode,
    PcmAlarms,
)
CONSUMERS_MODULE_DESCRIPTION = ModuleDescription(
    ConsumersSensorValues,
    ConsumersControlValues,
    ConsumersParameters,
    ConsumersControl,
    ConsumersControlMode,
    ConsumersAlarms,
)

MODES: dict[str, tuple[str, CombinedModule]] = {
    "thrusters": (
        thrusters_path,
        CombinedModule(
            {
                "thrusters": THRUSTERS_MODULE_DESCRIPTION,
            },
            ThrustersSimulationInputs,
            ThrustersSimulationOutputs,
            control_topic_suffix=settings.mqtt_control_topic_suffix,
        ),
    ),
    "pvt": (
        pvt_path,
        CombinedModule(
            {"pvt": PVT_MODULE_DESCRIPTION},
            PvtSimulationInputs,
            PvtSimulationOutputs,
            control_topic_suffix=settings.mqtt_control_topic_suffix,
        ),
    ),
    "pcm": (
        pcm_path,
        CombinedModule(
            {"pcm": PCM_MODULE_DESCRIPTION},
            PcmSimulationInputs,
            PcmSimulationOutputs,
            control_topic_suffix=settings.mqtt_control_topic_suffix,
        ),
    ),
    "consumers": (
        consumers_path,
        CombinedModule(
            {"consumers": CONSUMERS_MODULE_DESCRIPTION},
            ConsumersSimulationInputs,
            ConsumersSimulationOutputs,
            control_topic_suffix=settings.mqtt_control_topic_suffix,
        ),
    ),
    "high_temperature": (
        high_temperature_path,
        HighTemperatureModule(control_topic_suffix=settings.mqtt_control_topic_suffix),
    ),
}

Modes = Literal["thrusters", "pvt", "pcm", "consumers", "high_temperature"]


@dataclass
class MqttContext:
    topic: str

    @property
    def module(self) -> str:
        return self.topic.split("/")[0]


@dataclass
class MessageContext[
    SensorValues: ThrsValues,
    ControlValues: ThrsValues,
    Parameters: ThrsValues,
    Inputs: SimulationInputs,
    Outputs: SimulationValues,
]:
    cmds: "Queue[SimulationCtrlMessage]"
    control: CombinedControl
    client: MqttClient
    executor: SimulationExecutor[
        SensorValues,
        ControlValues,
        Inputs,
        Outputs,
    ]
    topic_prefix: str

    async def send(self, message: "OutgoingMessage"):
        await self.client.publish(
            f"{self.topic_prefix}/{message.topic()}",
            message.model_dump_json(),
            qos=1,
            retain=message.retained(),
        )


class IncomingMessage(ThrsValues):
    @staticmethod
    @abstractmethod
    def resolve[
        ControlValues: ThrsValues,
        Parameters: ThrsValues,
        Inputs: SimulationInputs,
        Outputs: SimulationValues,
    ](
        control_values: type[ControlValues],
        parameters: type[Parameters],
        simulation_inputs: type[Inputs],
        simulation_outputs: type[Outputs],
    ) -> "type[IncomingMessage]": ...

    @staticmethod
    @abstractmethod
    def subscribe_topic() -> str: ...

    def topic(self) -> str:
        return self.subscribe_topic()

    @abstractmethod
    async def handle(self, context: MessageContext): ...


class IncomingModuleMessage(IncomingMessage):
    module: Annotated[str, Field(exclude=True, default=None)]

    @model_validator(mode="before")
    @classmethod
    def module_from_topic(cls, data: Any, info: ValidationInfo[MqttContext]) -> Any:
        if "module" not in data and info.context:
            data["module"] = info.context.module
        return data


class OutgoingMessage(ThrsValues):
    @staticmethod
    @abstractmethod
    def subscribe_topic() -> str: ...

    @staticmethod
    @abstractmethod
    def retained() -> bool: ...

    def topic(self) -> str:
        return self.subscribe_topic()

    @classmethod
    def clear_topics(cls, modules: list[str]) -> list[str]:
        return [cls.subscribe_topic()]


class SimulationStatusMessage(OutgoingMessage):
    mode: str
    status: Literal["available", "running", "stepping"]
    control_modules: list[str]
    simulation_time: datetime

    @staticmethod
    def subscribe_topic() -> str:
        return "simulation/status"

    @staticmethod
    def retained() -> bool:
        return True


class ControlModeMessage[ControlMode](OutgoingMessage):
    module: str
    mode: SwitchingControlMode[ControlMode]

    @staticmethod
    def subscribe_topic() -> str:
        return "+/controls/status"

    def topic(self) -> str:
        return f"{self.module}/controls/status"

    @classmethod
    def clear_topics(cls, control_modules: list[str]) -> list[str]:
        return [f"{module}/controls/status" for module in control_modules]

    @staticmethod
    def retained() -> bool:
        return True


class ParametersMessage[Parameters: ThrsValues](OutgoingMessage):
    parameters: Parameters
    module: str

    @staticmethod
    def subscribe_topic() -> str:
        return "+/config/parameters"

    def topic(self) -> str:
        return f"{self.module}/config/parameters"

    @classmethod
    def clear_topics(cls, modules: list[str]) -> list[str]:
        return [f"{module}/config/parameters" for module in modules]

    @staticmethod
    def retained() -> bool:
        return True


class SimulationInputMessage[Inputs: ThrsValues](OutgoingMessage):
    inputs: Inputs

    @staticmethod
    def subscribe_topic() -> str:
        return "simulation/inputs"

    @staticmethod
    def retained() -> bool:
        return True


OUTGOING_MESSAGES = [
    SimulationStatusMessage,
    ControlModeMessage,
    ParametersMessage,
    SimulationInputMessage,
]


class SimulationCtrlMessage(IncomingMessage):
    async def handle(self, context: MessageContext):
        await context.cmds.put(self)


class PlayMessage(SimulationCtrlMessage):
    playback_rate: Annotated[float, Field(ge=0.25, le=10)] = 1.0

    @staticmethod
    def resolve[
        ControlValues: ThrsValues,
        Parameters: ThrsValues,
        Inputs: SimulationInputs,
        Outputs: SimulationValues,
    ](
        control_values: type[ControlValues],
        parameters: type[Parameters],
        simulation_inputs: type[Inputs],
        simulation_outputs: type[Outputs],
    ) -> "type[IncomingMessage]":
        return PlayMessage

    @staticmethod
    def subscribe_topic() -> str:
        return "simulation/play"


class StepMessage(SimulationCtrlMessage):
    seconds: Annotated[float, Field(ge=0)]

    @staticmethod
    def resolve[
        ControlValues: ThrsValues,
        Parameters: ThrsValues,
        Inputs: SimulationInputs,
        Outputs: SimulationValues,
    ](
        control_values: type[ControlValues],
        parameters: type[Parameters],
        simulation_inputs: type[Inputs],
        simulation_outputs: type[Outputs],
    ) -> "type[IncomingMessage]":
        return StepMessage

    @staticmethod
    def subscribe_topic() -> str:
        return "simulation/step"


class PauseMessage(SimulationCtrlMessage):
    @staticmethod
    def resolve[
        ControlValues: ThrsValues,
        Parameters: ThrsValues,
        Inputs: SimulationInputs,
        Outputs: SimulationValues,
    ](
        control_values: type[ControlValues],
        parameters: type[Parameters],
        simulation_inputs: type[Inputs],
        simulation_outputs: type[Outputs],
    ) -> "type[IncomingMessage]":
        return PauseMessage

    @staticmethod
    def subscribe_topic() -> str:
        return "simulation/pause"


class ManualControlMessage[ControlValues: ThrsValues](IncomingModuleMessage):
    control_values: ControlValues

    @staticmethod
    def resolve[
        LControlValues: ThrsValues,
        Parameters: ThrsValues,
        Inputs: SimulationInputs,
        Outputs: SimulationValues,
    ](
        control_values: type[LControlValues],
        parameters: type[Parameters],
        simulation_inputs: type[Inputs],
        simulation_outputs: type[Outputs],
    ) -> "type[IncomingMessage]":
        return ManualControlMessage[control_values]

    @staticmethod
    def subscribe_topic() -> str:
        return "+/controls/manual"

    def topic(self):
        return f"{self.module}/controls/manual"

    async def handle(
        self,
        context: MessageContext[
            ThrsValues, ControlValues, ThrsValues, SimulationInputs, SimulationValues
        ],
    ):
        context.control.manual_controls(self.module, self.control_values)


class SetAutomationMessage(IncomingModuleMessage):
    enabled: bool

    @staticmethod
    def resolve[
        ControlValues: ThrsValues,
        Parameters: ThrsValues,
        Inputs: SimulationInputs,
        Outputs: SimulationValues,
    ](
        control_values: type[ControlValues],
        parameters: type[Parameters],
        simulation_inputs: type[Inputs],
        simulation_outputs: type[Outputs],
    ) -> "type[IncomingMessage]":
        return SetAutomationMessage

    @staticmethod
    def subscribe_topic() -> str:
        return "+/controls/set_automation"

    def topic(self):
        return f"{self.module}/controls/set_automation"

    async def handle(self, context: MessageContext):
        context.control.set_automation_mode(self.module, self.enabled)
        await context.send(
            ControlModeMessage(
                module=self.module,
                mode=context.control.mode_for(self.module),
            )
        )


class SetParametersMessage[Parameters: ThrsValues](IncomingModuleMessage):
    parameters: Parameters

    @staticmethod
    def resolve[
        ControlValues: ThrsValues,
        LParameters: ThrsValues,
        Inputs: SimulationInputs,
        Outputs: SimulationValues,
    ](
        control_values: type[ControlValues],
        parameters: type[LParameters],
        simulation_inputs: type[Inputs],
        simulation_outputs: type[Outputs],
    ) -> "type[IncomingMessage]":
        return SetParametersMessage[parameters]

    @staticmethod
    def subscribe_topic() -> str:
        return "+/controls/set_parameters"

    def topic(self):
        return f"{self.module}/controls/set_parameters"

    async def handle(self, context: MessageContext[Any, Any, Parameters, Any, Any]):
        context.control.update_parameters_for(self.module, self.parameters)
        await context.send(
            ParametersMessage(
                parameters=context.control.parameters.values[self.module],
                module=self.module,
            )
        )


class SetSimulationInputsMessage[Inputs: SimulationInputs](IncomingMessage):
    inputs: Inputs

    @staticmethod
    def resolve[
        ControlValues: ThrsValues,
        Parameters: ThrsValues,
        LInputs: SimulationInputs,
        Outputs: SimulationValues,
    ](
        control_values: type[ControlValues],
        parameters: type[Parameters],
        simulation_inputs: type[LInputs],
        simulation_outputs: type[Outputs],
    ) -> "type[IncomingMessage]":
        return SetSimulationInputsMessage[simulation_inputs]

    @staticmethod
    def subscribe_topic() -> str:
        return "simulation/set_inputs"

    async def handle(self, context: MessageContext):
        context.executor.update_simulation_inputs(self.inputs)
        await context.send(SimulationInputMessage(inputs=self.inputs))


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
        topic_prefix: str,
    ):
        self._sensor_client = sensor_client
        self._control_client = control_client
        self._controls_client = controls_client
        self._topic_prefix = topic_prefix

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
                topic_prefix=settings.mqtt_topic_prefix,
            )

    async def _receive_controls(
        self,
        handlers: list[IncomingMessage],
        context: MessageContext,
        modules: CombinedModule,
    ):
        async for message in self._controls_client.messages:
            for handler in handlers:
                if message.topic.matches(
                    f"{self._topic_prefix}/{handler.subscribe_topic()}"
                ) and isinstance(message.payload, str | bytes):
                    logger.debug(
                        f"Received message on topic {message.topic}, handling {handler}"
                    )
                    mqtt_context = MqttContext(
                        topic=message.topic.value.removeprefix(
                            f"{self._topic_prefix}/"
                        ),
                    )
                    resolved_handler = (
                        handler.resolve(
                            modules.control_values_for_module(mqtt_context.module),
                            modules.parameters_for_module(mqtt_context.module),
                            modules.simulation_inputs_cls,
                            modules.simulation_outputs_cls,
                        )
                        if mqtt_context.module in modules.modules
                        else handler.resolve(
                            ThrsValues,
                            ThrsValues,
                            modules.simulation_inputs_cls,
                            modules.simulation_outputs_cls,
                        )
                    )

                    await resolved_handler.model_validate_json(
                        message.payload,
                        context=MqttContext(
                            topic=message.topic.value.removeprefix(
                                f"{self._topic_prefix}/"
                            ),
                        ),
                    ).handle(context)
                    break

    async def clear_previous(self):
        all_modules = list(
            set(
                module
                for _fmu_path, nesting in MODES.values()
                for module in nesting.modules
            )
        )
        for msg_cls in OUTGOING_MESSAGES:
            if msg_cls.retained():
                for topic in msg_cls.clear_topics(all_modules):
                    await self._controls_client.publish(
                        f"{self._topic_prefix}/{topic}", None, qos=1, retain=True
                    )

    @contextmanager
    def _executor(
        self, fmu_path: str, modules: CombinedModule, inputs: SimulationInputs
    ) -> Generator[SimulationExecutor, None, None]:
        with Fmu(fmu_path) as fmu:
            yield SimulationExecutor(
                modules.io_mapping(), fmu, inputs, datetime.now(), timedelta(seconds=1)
            )

    async def run(self, mode: Modes):
        for handler in HANDLERS:
            await self._controls_client.subscribe(
                f"{self._topic_prefix}/{handler.subscribe_topic()}", qos=1
            )

        fmu_path, modules = MODES[mode]
        simulation_inputs = INPUTS[mode]

        with self._executor(fmu_path, modules, simulation_inputs) as inner_executor:
            parameters = {module: CONTROL_PARAMS[module] for module in modules.modules}
            control = modules.control(CombinedValues(parameters), inner_executor.time)

            cmds: Queue[SimulationCtrlMessage] = Queue()
            context = MessageContext(
                cmds, control, self._controls_client, inner_executor, self._topic_prefix
            )
            for module in modules.modules:
                await context.send(
                    ControlModeMessage(module=module, mode=control.mode_for(module))
                )

            executor = MqttExecutor(
                inner_executor,
                self._control_client,
                self._sensor_client,
                self._topic_prefix,
                modules,
            )
            simulator = Simulator(executor, control, modules.alarms())

            await executor.start()
            executor_task = create_task(executor.run())
            receive_task = create_task(
                self._receive_controls(HANDLERS, context, modules)
            )
            try:
                for module in modules.modules:
                    await context.send(
                        ParametersMessage(
                            module=module,
                            parameters=control.parameters.values[module],
                        )
                    )
                await context.send(
                    SimulationInputMessage(
                        inputs=cast(ThrustersSimulationInputs, simulation_inputs)
                    )
                )
                await self._run_simulation(
                    mode, modules, context, executor, simulator, cmds
                )
            except Exception as e:
                logger.error(f"SimulationControls run encountered an error: {e}")
            finally:
                executor_task.cancel()
                receive_task.cancel()

    async def _run_simulation(
        self,
        mode: Modes,
        modules: CombinedModule,
        context: MessageContext,
        executor: MqttExecutor,
        simulator: Simulator,
        cmds: Queue[SimulationCtrlMessage],
    ):
        logging.debug("Simulation control loop started")
        active_modules = modules.modules
        while True:
            await context.send(
                SimulationStatusMessage(
                    mode=mode,
                    status="available",
                    simulation_time=executor.time(),
                    control_modules=active_modules,
                )
            )
            cmd = await cmds.get()
            if isinstance(cmd, PlayMessage):
                sleep_duration = (
                    context.executor.tick_duration.total_seconds() / cmd.playback_rate
                )
                await context.send(
                    SimulationStatusMessage(
                        mode=mode,
                        status="running",
                        simulation_time=executor.time(),
                        control_modules=active_modules,
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
                await context.send(
                    SimulationStatusMessage(
                        mode=mode,
                        status="stepping",
                        simulation_time=executor.time(),
                        control_modules=active_modules,
                    )
                )

                ticks = max(
                    1, int(cmd.seconds / context.executor.tick_duration.total_seconds())
                )
                logging.debug(f"Stepping simulation by {ticks} ticks")
                await simulator.run(ticks)
