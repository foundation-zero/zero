import logging
from abc import abstractmethod
from asyncio import Queue, TaskGroup, create_task, sleep
from contextlib import asynccontextmanager, nullcontext
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import (
    Annotated,
    Any,
    Callable,
    Literal,
    cast,
)

from aiomqtt import Client as MqttClient
from aiomqtt import Message
from pydantic import (
    Field,
    ValidationInfo,
    model_validator,
)

from thrs.control.modules.adsorption import ADSORPTION_MODULE_DESCRIPTION
from thrs.control.modules.consumers import CONSUMERS_MODULE_DESCRIPTION
from thrs.control.modules.dc import DC_MODULE_DESCRIPTION
from thrs.control.modules.dhw import DHW_MODULE_DESCRIPTION
from thrs.control.modules.drives import DRIVES_MODULE_DESCRIPTION
from thrs.control.modules.pcm import PCM_MODULE_DESCRIPTION
from thrs.control.modules.pvt import PVT_MODULE_DESCRIPTION
from thrs.control.modules.thrusters import THRUSTERS_MODULE_DESCRIPTION
from thrs.control.switching import SwitchingControlMode
from thrs.input_output.base import (
    CombinedValues,
    SimulationInputs,
    SimulationValues,
    Stamped,
    ThrsValues,
)
from thrs.input_output.definitions.simulation import (
    AdsorptionChiller,
    Boundary,
    Converter,
    FlowBoundary,
    HeatSource,
    HvacExchanger,
    OverpressureTemperatureBoundary,
    Pcs,
    PropulsionDrive,
    TemperatureBoundary,
    Thruster,
)
from thrs.input_output.definitions.units import PcsMode
from thrs.input_output.modules.adsorption import (
    AdsorptionSimulationInputs,
    AdsorptionSimulationOutputs,
)
from thrs.input_output.modules.consumers import (
    ConsumersSimulationInputs,
    ConsumersSimulationOutputs,
)
from thrs.input_output.modules.dc import DcSimulationInputs, DcSimulationOutputs
from thrs.input_output.modules.dhw import (
    DhwSimulationInputs,
    DhwSimulationOutputs,
)
from thrs.input_output.modules.drives import (
    DrivesSimulationInputs,
    DrivesSimulationOutputs,
)
from thrs.input_output.modules.high_temperature import (
    HighTemperatureSimulationInputs,
    HighTemperatureSimulationOutputs,
)
from thrs.input_output.modules.pcm import PcmSimulationInputs, PcmSimulationOutputs
from thrs.input_output.modules.pvt import PvtSimulationInputs, PvtSimulationOutputs
from thrs.input_output.modules.thrusters import (
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
from thrs.orchestration.config import Config
from thrs.orchestration.connector import (
    MqttConnector,
)
from thrs.orchestration.module import CombinedControl, CombinedModule
from thrs.orchestration.runner import Runner
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import (
    adsorption_path,
    consumers_path,
    dc_path,
    dhw_path,
    drives_path,
    high_temperature_path,
    pcm_path,
    pvt_path,
    thrusters_path,
)

logger = logging.getLogger(__name__)


SEAWATER_TEMPERATURE = 20.0

INPUTS = {
    "thrusters": ThrustersSimulationInputs(
        thrusters_thruster_aft=Thruster(
            heat_flow=Stamped.stamp(9000.0), active=Stamped.stamp(True)
        ),
        thrusters_thruster_fwd=Thruster(
            heat_flow=Stamped.stamp(4300.0), active=Stamped.stamp(True)
        ),
        thrusters_seawater_supply=Boundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE), flow=Stamped.stamp(64.0)
        ),
        thrusters_pcm_supply=TemperatureBoundary(temperature=Stamped.stamp(40.0)),
        thrusters_pcs=Pcs(mode=Stamped.stamp(PcsMode.PROPULSION)),
    ),
    "pvt": PvtSimulationInputs(
        pvt_main_fwd=HeatSource(heat_flow=Stamped.stamp(0)),
        pvt_main_aft=HeatSource(heat_flow=Stamped.stamp(0)),
        pvt_owners=HeatSource(heat_flow=Stamped.stamp(0)),
        pvt_pcm_supply=TemperatureBoundary(temperature=Stamped.stamp(50)),
        pvt_seawater_supply=Boundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE), flow=Stamped.stamp(50)
        ),
    ),
    "pcm": PcmSimulationInputs(
        pcm_thrusters_supply=Boundary(
            temperature=Stamped.stamp(70), flow=Stamped.stamp(80)
        ),
        pcm_consumers_supply=TemperatureBoundary(temperature=Stamped.stamp(30)),
        pcm_freshwater_supply=Boundary(
            temperature=Stamped.stamp(40), flow=Stamped.stamp(0)
        ),
    ),
    "consumers": ConsumersSimulationInputs(
        consumers_dhw_supply=Boundary(
            temperature=Stamped.stamp(30.0),
            flow=Stamped.stamp(10.0),
        ),
        consumers_adsorption_supply=Boundary(
            temperature=Stamped.stamp(30.0),
            flow=Stamped.stamp(10.0),
        ),
        consumers_pcm_supply=Boundary(
            temperature=Stamped.stamp(60.0), flow=Stamped.stamp(10.0)
        ),
    ),
    "adsorption": AdsorptionSimulationInputs(
        adsorption_cooling_supply=TemperatureBoundary(temperature=Stamped.stamp(20.0)),
        adsorption_seawater_supply=Boundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE), flow=Stamped.stamp(64.0)
        ),
        adsorption_available_cold_temperature=TemperatureBoundary(
            temperature=Stamped.stamp(20.0)
        ),
        adsorption_available_hot_temperature=TemperatureBoundary(
            temperature=Stamped.stamp(65.0)
        ),
        adsorption_available_seawater_temperature=TemperatureBoundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE)
        ),
        adsorption_chiller=AdsorptionChiller(free_cooling=Stamped.stamp(False)),
        adsorption_ht_supply=Boundary(
            temperature=Stamped.stamp(60.0), flow=Stamped.stamp(42.0)
        ),
        adsorption_dhw_supply=Boundary(
            temperature=Stamped.stamp(40.0), flow=Stamped.stamp(45.0)
        ),
    ),
    "drives": DrivesSimulationInputs(
        drives_oil_cooler_aft=HeatSource(heat_flow=Stamped.stamp(0)),
        drives_oil_cooler_fwd=HeatSource(heat_flow=Stamped.stamp(0)),
        drives_propdrive_aft1=PropulsionDrive(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        drives_propdrive_aft2=PropulsionDrive(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        drives_propdrive_fwd1=PropulsionDrive(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        drives_propdrive_fwd2=PropulsionDrive(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        drives_shorepower=Converter(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        drives_seawater_supply=Boundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE), flow=Stamped.stamp(64)
        ),
        drives_dhw_supply=Boundary(
            temperature=Stamped.stamp(20), flow=Stamped.stamp(29)
        ),
    ),
    "dc": DcSimulationInputs(
        dc_brightloop_fwd1=Converter(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        dc_brightloop_fwd2=Converter(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        dc_ugrid1=Converter(heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)),
        dc_ugrid2=Converter(heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)),
        dc_brightloop_aft1=Converter(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        dc_brightloop_aft2=Converter(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        dc_brightloop_aft3=Converter(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        dc_brightloop_aft4=Converter(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        dc_seawater_supply=Boundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE), flow=Stamped.stamp(64)
        ),
        dc_dhw_supply=Boundary(temperature=Stamped.stamp(35), flow=Stamped.stamp(20)),
    ),
    "high_temperature": HighTemperatureSimulationInputs(
        thrusters_thruster_aft=Thruster(
            heat_flow=Stamped.stamp(9000.0), active=Stamped.stamp(True)
        ),
        thrusters_thruster_fwd=Thruster(
            heat_flow=Stamped.stamp(0.0), active=Stamped.stamp(True)
        ),
        thrusters_seawater_supply=Boundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE),
            flow=Stamped.stamp(64.0),
        ),
        thrusters_pcs=Pcs(mode=Stamped.stamp(PcsMode.PROPULSION)),
        pvt_main_fwd=HeatSource(heat_flow=Stamped.stamp(0)),
        pvt_main_aft=HeatSource(heat_flow=Stamped.stamp(0)),
        pvt_owners=HeatSource(heat_flow=Stamped.stamp(0)),
        pvt_seawater_supply=Boundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE), flow=Stamped.stamp(50)
        ),
        pcm_freshwater_supply=Boundary(
            temperature=Stamped.stamp(40.0),
            flow=Stamped.stamp(0.0),
        ),
        consumers_adsorption_supply=Boundary(
            temperature=Stamped.stamp(30.0),
            flow=Stamped.stamp(0.0),
        ),
        consumers_dhw_supply=Boundary(
            temperature=Stamped.stamp(30.0),
            flow=Stamped.stamp(0.0),
        ),
    ),
    "dhw": DhwSimulationInputs(
        dhw_drives_supply=Boundary(
            temperature=Stamped.stamp(50),
            flow=Stamped.stamp(35),
        ),
        dhw_dc_supply=Boundary(
            temperature=Stamped.stamp(60),
            flow=Stamped.stamp(60),
        ),
        dhw_adsorption_supply=Boundary(
            temperature=Stamped.stamp(40),
            flow=Stamped.stamp(45),
        ),
        dhw_ht_supply=Boundary(
            temperature=Stamped.stamp(60),
            flow=Stamped.stamp(60),
        ),
        dhw_freshwater_supply=OverpressureTemperatureBoundary(
            temperature=Stamped.stamp(20),
            overpressure=Stamped.stamp(3),
        ),
        dhw_hvac_exchanger=HvacExchanger(
            heat_flow=Stamped.stamp(300), maximum_temperature=Stamped.stamp(36)
        ),
        dhw_seawater_supply=TemperatureBoundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE)
        ),
        dhw_hotwater_demand=FlowBoundary(flow=Stamped.stamp(30)),
    ),
}


type Modes = Literal[
    "thrusters",
    "pvt",
    "pcm",
    "consumers",
    "adsorption",
    "drives",
    "dc",
    "high_temperature",
    "dhw",
    "boat",
]

MODES: dict[Modes, tuple[str | None, CombinedModule]] = {
    "boat": (
        None,
        CombinedModule(
            {
                "thrusters": THRUSTERS_MODULE_DESCRIPTION,
                "pvt": PVT_MODULE_DESCRIPTION,
                "pcm": PCM_MODULE_DESCRIPTION,
                "consumers": CONSUMERS_MODULE_DESCRIPTION,
                "adsorption": ADSORPTION_MODULE_DESCRIPTION,
                "drives": DRIVES_MODULE_DESCRIPTION,
                "dc": DC_MODULE_DESCRIPTION,
                "dhw": DHW_MODULE_DESCRIPTION,
            },
            None,
            None,
        ),
    ),
    "thrusters": (
        thrusters_path,
        CombinedModule(
            {
                "thrusters": THRUSTERS_MODULE_DESCRIPTION,
            },
            ThrustersSimulationInputs,
            ThrustersSimulationOutputs,
        ),
    ),
    "pvt": (
        pvt_path,
        CombinedModule(
            {"pvt": PVT_MODULE_DESCRIPTION},
            PvtSimulationInputs,
            PvtSimulationOutputs,
        ),
    ),
    "pcm": (
        pcm_path,
        CombinedModule(
            {"pcm": PCM_MODULE_DESCRIPTION},
            PcmSimulationInputs,
            PcmSimulationOutputs,
        ),
    ),
    "consumers": (
        consumers_path,
        CombinedModule(
            {"consumers": CONSUMERS_MODULE_DESCRIPTION},
            ConsumersSimulationInputs,
            ConsumersSimulationOutputs,
        ),
    ),
    "adsorption": (
        adsorption_path,
        CombinedModule(
            {"adsorption": ADSORPTION_MODULE_DESCRIPTION},
            AdsorptionSimulationInputs,
            AdsorptionSimulationOutputs,
        ),
    ),
    "drives": (
        drives_path,
        CombinedModule(
            {"drives": DRIVES_MODULE_DESCRIPTION},
            DrivesSimulationInputs,
            DrivesSimulationOutputs,
        ),
    ),
    "dc": (
        dc_path,
        CombinedModule(
            {"dc": DC_MODULE_DESCRIPTION},
            DcSimulationInputs,
            DcSimulationOutputs,
        ),
    ),
    "high_temperature": (
        high_temperature_path,
        CombinedModule(
            {
                "thrusters": THRUSTERS_MODULE_DESCRIPTION,
                "pvt": PVT_MODULE_DESCRIPTION,
                "pcm": PCM_MODULE_DESCRIPTION,
                "consumers": CONSUMERS_MODULE_DESCRIPTION,
            },
            HighTemperatureSimulationInputs,
            HighTemperatureSimulationOutputs,
        ),
    ),
    "dhw": (
        dhw_path,
        CombinedModule(
            {"dhw": DHW_MODULE_DESCRIPTION},
            DhwSimulationInputs,
            DhwSimulationOutputs,
        ),
    ),
}


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
    Inputs: SimulationInputs,
    Outputs: SimulationValues,
]:
    cmds: "Queue[SimulationCtrlMessage]"
    control: CombinedControl
    client: MqttClient
    simulation: (
        Simulation[
            SensorValues,
            ControlValues,
            Inputs,
            Outputs,
        ]
        | None
    )

    async def send(self, topic_prefix: str, message: "OutgoingMessage"):
        await self.client.publish(
            f"{topic_prefix}/{message.topic()}",
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
        simulation_inputs: type[Inputs] | None,
        simulation_outputs: type[Outputs] | None,
    ) -> "type[IncomingMessage] | None": ...

    @staticmethod
    @abstractmethod
    def subscribe_topic() -> str: ...

    def topic(self) -> str:
        return self.subscribe_topic()

    @abstractmethod
    async def handle(self, topic_prefix: str, context: MessageContext): ...


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
    def clear_topics(cls, control_modules: list[str]) -> list[str]:
        return [cls.subscribe_topic()]


class SimulationStatusMessage(OutgoingMessage):
    mode: str
    status: Literal["available", "running", "stepping"]
    control_modules: list[str]
    simulation_time: datetime

    @staticmethod
    def subscribe_topic() -> str:
        return "status"

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
    def clear_topics(cls, control_modules: list[str]) -> list[str]:
        return [f"{module}/config/parameters" for module in control_modules]

    @staticmethod
    def retained() -> bool:
        return True


class SimulationInputMessage[Inputs: ThrsValues](OutgoingMessage):
    inputs: Inputs

    @staticmethod
    def subscribe_topic() -> str:
        return "inputs"

    @staticmethod
    def retained() -> bool:
        return True


SIMULATION_OUTGOING_MESSAGES = [
    SimulationStatusMessage,
    SimulationInputMessage,
]

CONTROLLER_OUTGOING_MESSAGES = [
    ControlModeMessage,
    ParametersMessage,
]


class SimulationCtrlMessage(IncomingMessage):
    async def handle(self, topic_prefix: str, context: MessageContext):
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
        simulation_inputs: type[Inputs] | None,
        simulation_outputs: type[Outputs] | None,
    ) -> "type[IncomingMessage] | None":
        return PlayMessage

    @staticmethod
    def subscribe_topic() -> str:
        return "play"


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
        simulation_inputs: type[Inputs] | None,
        simulation_outputs: type[Outputs] | None,
    ) -> "type[IncomingMessage] | None":
        return StepMessage

    @staticmethod
    def subscribe_topic() -> str:
        return "step"


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
        simulation_inputs: type[Inputs] | None,
        simulation_outputs: type[Outputs] | None,
    ) -> "type[IncomingMessage] | None":
        return PauseMessage

    @staticmethod
    def subscribe_topic() -> str:
        return "pause"


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
        simulation_inputs: type[Inputs] | None,
        simulation_outputs: type[Outputs] | None,
    ) -> "type[IncomingMessage] | None":
        return ManualControlMessage[control_values]

    @staticmethod
    def subscribe_topic() -> str:
        return "+/controls/manual"

    def topic(self):
        return f"{self.module}/controls/manual"

    async def handle(
        self,
        topic_prefix: str,
        context: MessageContext[
            ThrsValues, ControlValues, SimulationInputs, SimulationValues
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
        simulation_inputs: type[Inputs] | None,
        simulation_outputs: type[Outputs] | None,
    ) -> "type[IncomingMessage] | None":
        return SetAutomationMessage

    @staticmethod
    def subscribe_topic() -> str:
        return "+/controls/set_automation"

    def topic(self):
        return f"{self.module}/controls/set_automation"

    async def handle(self, topic_prefix: str, context: MessageContext):
        context.control.set_automation_mode(self.module, self.enabled)
        await context.send(
            topic_prefix,
            ControlModeMessage(
                module=self.module,
                mode=context.control.mode_for(self.module),
            ),
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
        simulation_inputs: type[Inputs] | None,
        simulation_outputs: type[Outputs] | None,
    ) -> "type[IncomingMessage] | None":
        return SetParametersMessage[parameters]

    @staticmethod
    def subscribe_topic() -> str:
        return "+/controls/set_parameters"

    def topic(self):
        return f"{self.module}/controls/set_parameters"

    async def handle(
        self, topic_prefix: str, context: MessageContext[Any, Any, Any, Any]
    ):
        context.control.update_parameters_for(self.module, self.parameters)
        await context.send(
            topic_prefix,
            ParametersMessage(
                parameters=context.control.parameters.values[self.module],
                module=self.module,
            ),
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
        simulation_inputs: type[LInputs] | None,
        simulation_outputs: type[Outputs] | None,
    ) -> "type[IncomingMessage] | None":
        if simulation_inputs is None:
            return None

        return SetSimulationInputsMessage[simulation_inputs]

    @staticmethod
    def subscribe_topic() -> str:
        return "set_inputs"

    async def handle(self, topic_prefix: str, context: MessageContext):
        if context.simulation:
            context.simulation.update_simulation_inputs(self.inputs)
            await context.send(topic_prefix, SimulationInputMessage(inputs=self.inputs))


SIMULATION_HANDLERS = [
    PlayMessage,
    StepMessage,
    PauseMessage,
    SetSimulationInputsMessage,
]

CONTROLLER_HANDLERS = [
    ManualControlMessage,
    SetAutomationMessage,
    SetParametersMessage,
]


class SimulationControls:
    def __init__(
        self,
        controls_client: MqttClient,
        control_client: MqttClient,
        sensor_client: MqttClient,
        devices_topic_prefix: str,
        controller_topic_prefix: str,
        simulation_topic_prefix: str,
        control_topic_suffix: str,
    ):
        self._sensor_client = sensor_client
        self._control_client = control_client
        self._controls_client = controls_client
        self._devices_topic_prefix = devices_topic_prefix
        self._controller_topic_prefix = controller_topic_prefix
        self._simulation_topic_prefix = simulation_topic_prefix
        self._control_topic_suffix = control_topic_suffix

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
                devices_topic_prefix=settings.mqtt_devices_topic_prefix,
                controller_topic_prefix=settings.mqtt_controller_topic_prefix,
                simulation_topic_prefix=settings.mqtt_simulation_topic_prefix,
                control_topic_suffix=settings.mqtt_control_topic_suffix,
            )

    async def _handle_message(
        self,
        message: Message,
        handlers: list[type[IncomingMessage]],
        topic_prefix: str,
        context: MessageContext,
        modules: CombinedModule,
    ) -> bool:
        for handler in handlers:
            if message.topic.matches(
                f"{topic_prefix}/{handler.subscribe_topic()}"
            ) and isinstance(message.payload, str | bytes):
                logger.debug(
                    f"Received message on topic {message.topic}, handling {handler}"
                )
                mqtt_context = MqttContext(
                    topic=message.topic.value.removeprefix(f"{topic_prefix}/"),
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

                if resolved_handler:
                    await resolved_handler.model_validate_json(
                        message.payload, context=mqtt_context
                    ).handle(topic_prefix, context)
                return True
        return False

    async def _receive_controls(
        self,
        simulation_handlers: list[type[IncomingMessage]],
        controller_handlers: list[type[IncomingMessage]],
        simulation_topic_prefix: str,
        controller_topic_prefix: str,
        context: MessageContext,
        modules: CombinedModule,
    ):
        async for message in self._controls_client.messages:
            handled = await self._handle_message(
                message, simulation_handlers, simulation_topic_prefix, context, modules
            )
            if not handled:
                await self._handle_message(
                    message,
                    controller_handlers,
                    controller_topic_prefix,
                    context,
                    modules,
                )

    async def clear_previous(self):
        all_modules = list(
            set(
                module
                for _fmu_path, nesting in MODES.values()
                for module in nesting.modules
            )
        )
        for msg_cls in SIMULATION_OUTGOING_MESSAGES:
            if msg_cls.retained():
                for topic in msg_cls.clear_topics(all_modules):
                    await self._controls_client.publish(
                        f"{self._simulation_topic_prefix}/{topic}",
                        None,
                        qos=1,
                        retain=True,
                    )
        for msg_cls in CONTROLLER_OUTGOING_MESSAGES:
            if msg_cls.retained():
                for topic in msg_cls.clear_topics(all_modules):
                    await self._controls_client.publish(
                        f"{self._controller_topic_prefix}/{topic}",
                        None,
                        qos=1,
                        retain=True,
                    )

    async def run(self, mode: Modes):
        logger.info(f"Starting simulation in mode: {mode}")

        for handler in SIMULATION_HANDLERS:
            await self._controls_client.subscribe(
                f"{self._simulation_topic_prefix}/{handler.subscribe_topic()}", qos=1
            )
        for handler in CONTROLLER_HANDLERS:
            await self._controls_client.subscribe(
                f"{self._controller_topic_prefix}/{handler.subscribe_topic()}", qos=1
            )

        fmu_path, modules = MODES[mode]
        simulation_inputs = INPUTS[mode]

        fmu = Fmu(fmu_path) if fmu_path else nullcontext()

        with fmu as fmu:
            tick_duration = timedelta(seconds=1)

            if fmu and modules.simulation_outputs_cls:
                simulation = Simulation(
                    modules.sensor_values_clss,
                    modules.simulation_outputs_cls,
                    fmu,
                    simulation_inputs,
                    datetime.now(),
                    tick_duration,
                )
                time_func = simulation.time

                simulation_connector = MqttConnector(
                    mqtt_client=self._sensor_client,
                    devices_topic_prefix=self._devices_topic_prefix,
                    controller_topic_prefix=self._simulation_topic_prefix,
                    sensor_values_clss={},  # It actually does not listen to mqtt for these but gets them directly from the runner
                    control_values_clss=modules.sensor_values_clss,
                    controller_values_clss={mode: modules.simulation_outputs_cls},
                    sensor_topic_suffix=self._control_topic_suffix,
                )
                simulation_connector_task = create_task(simulation_connector.run())

            else:
                simulation = None
                time_func = datetime.now
                simulation_connector = None
                simulation_connector_task = None

            parameters = {
                module: modules.parameters_for_module(module)()
                for module in modules.modules
            }
            control = modules.control(CombinedValues(parameters), time_func)

            cmds: Queue[SimulationCtrlMessage] = Queue()
            context = MessageContext(cmds, control, self._controls_client, simulation)
            for module in modules.modules:
                await context.send(
                    self._controller_topic_prefix,
                    ControlModeMessage(module=module, mode=control.mode_for(module)),
                )

            control_connector = MqttConnector(
                mqtt_client=self._control_client,
                devices_topic_prefix=self._devices_topic_prefix,
                controller_topic_prefix=self._controller_topic_prefix,
                sensor_values_clss=modules.sensor_values_clss,
                control_values_clss=modules.control_values_clss,
                controller_values_clss={},  # Nothing yet, but we want to send controller values here at some point
                control_topic_suffix=self._control_topic_suffix,
            )

            runner = Runner(
                control_connector,
                mode,
                simulation,
                simulation_connector,
                control,  # type: ignore
                modules.alarms(),  # type: ignore
            )

            control_connector_task = create_task(control_connector.run())
            receive_task = create_task(
                self._receive_controls(
                    SIMULATION_HANDLERS,
                    CONTROLLER_HANDLERS,
                    self._simulation_topic_prefix,
                    self._controller_topic_prefix,
                    context,
                    modules,
                )
            )
            try:
                for module in modules.modules:
                    await context.send(
                        self._controller_topic_prefix,
                        ParametersMessage(
                            module=module,
                            parameters=control.parameters.values[module],
                        ),
                    )
                if simulation:
                    await context.send(
                        self._simulation_topic_prefix,
                        SimulationInputMessage(
                            inputs=cast(ThrustersSimulationInputs, simulation_inputs)
                        ),
                    )
                await self._run_simulation(
                    mode, modules, context, time_func, tick_duration, runner, cmds
                )
            except Exception as e:
                logger.exception(f"SimulationControls run encountered an error: {e}")
            finally:
                control_connector_task.cancel()
                if simulation_connector_task:
                    simulation_connector_task.cancel()
                receive_task.cancel()

    async def _run_simulation(
        self,
        mode: Modes,
        modules: CombinedModule,
        context: MessageContext,
        time_func: Callable[[], datetime],
        tick_duration: timedelta,
        runner: Runner,
        cmds: Queue[SimulationCtrlMessage],
    ):
        logging.debug("Simulation control loop started")
        active_modules = modules.modules
        while True:
            await context.send(
                self._simulation_topic_prefix,
                SimulationStatusMessage(
                    mode=mode,
                    status="available",
                    simulation_time=time_func(),
                    control_modules=active_modules,
                ),
            )
            cmd = await cmds.get()
            if isinstance(cmd, PlayMessage):
                sleep_duration = tick_duration.total_seconds() / cmd.playback_rate
                await context.send(
                    self._simulation_topic_prefix,
                    SimulationStatusMessage(
                        mode=mode,
                        status="running",
                        simulation_time=time_func(),
                        control_modules=active_modules,
                    ),
                )
                logging.debug(
                    f"Starting simulation with tick interval of {sleep_duration} seconds"
                )
                while cmds.empty():
                    async with TaskGroup() as tg:
                        tg.create_task(sleep(sleep_duration))
                        tg.create_task(runner.run(1))
                logger.debug("Simulation paused")
            elif isinstance(cmd, StepMessage):
                await context.send(
                    self._simulation_topic_prefix,
                    SimulationStatusMessage(
                        mode=mode,
                        status="stepping",
                        simulation_time=time_func(),
                        control_modules=active_modules,
                    ),
                )

                ticks = max(
                    1,
                    int(cmd.seconds / tick_duration.total_seconds()),
                )
                logging.debug(f"Stepping simulation by {ticks} ticks")
                await runner.run(ticks)
