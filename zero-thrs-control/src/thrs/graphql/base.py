from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from inspect import isclass

import strawberry
from pydantic.fields import FieldInfo
from strawberry.fastapi import BaseContext

from thrs.control.modules.adsorption import (
    AdsorptionControllerState,
    AdsorptionControlMode,
    AdsorptionParameters,
)
from thrs.control.modules.consumers import (
    ConsumersControllerState,
    ConsumersControlMode,
    ConsumersParameters,
)
from thrs.control.modules.dc import DcControllerState, DcControlMode, DcParameters
from thrs.control.modules.dhw import DhwControllerState, DhwControlMode, DhwParameters
from thrs.control.modules.drives import (
    DrivesControllerState,
    DrivesControlMode,
    DrivesParameters,
)
from thrs.control.modules.pcm import PcmControllerState, PcmControlMode, PcmParameters
from thrs.control.modules.pvt import PvtControllerState, PvtControlMode, PvtParameters
from thrs.control.modules.thrusters import (
    ThrustersControllerState,
    ThrustersControlMode,
    ThrustersParameters,
)
from thrs.control.switching import SwitchingControlMode
from thrs.graphql.helpers import ensure_input_type, optional_pydantic_to_graphql
from thrs.graphql.messaging import (
    ControlMessaging,
    DirectiveMessaging,
    SimulationMessaging,
)
from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions import (
    control,
    controllers,
    sensor,
    simulation,
    system,
)
from thrs.input_output.modules.adsorption import (
    AdsorptionControlValues,
    AdsorptionSensorValues,
)
from thrs.input_output.modules.consumers import (
    ConsumersControlValues,
    ConsumersSensorValues,
)
from thrs.input_output.modules.dc import DcControlValues, DcSensorValues
from thrs.input_output.modules.dhw import DhwControlValues, DhwSensorValues
from thrs.input_output.modules.drives import DrivesControlValues, DrivesSensorValues
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
)

type ThrustersMessaging = ControlMessaging[
    ThrustersSensorValues,
    ThrustersControlValues,
    ThrustersParameters,
    ThrustersControlMode,
    ThrustersControllerState,
]

type PvtMessaging = ControlMessaging[
    PvtSensorValues,
    PvtControlValues,
    PvtParameters,
    PvtControlMode,
    PvtControllerState,
]


type PcmMessaging = ControlMessaging[
    PcmSensorValues,
    PcmControlValues,
    PcmParameters,
    PcmControlMode,
    PcmControllerState,
]


type ConsumersMessaging = ControlMessaging[
    ConsumersSensorValues,
    ConsumersControlValues,
    ConsumersParameters,
    ConsumersControlMode,
    ConsumersControllerState,
]

type AdsorptionMessaging = ControlMessaging[
    AdsorptionSensorValues,
    AdsorptionControlValues,
    AdsorptionParameters,
    AdsorptionControlMode,
    AdsorptionControllerState,
]

type DrivesMessaging = ControlMessaging[
    DrivesSensorValues,
    DrivesControlValues,
    DrivesParameters,
    DrivesControlMode,
    DrivesControllerState,
]

type DcMessaging = ControlMessaging[
    DcSensorValues,
    DcControlValues,
    DcParameters,
    DcControlMode,
    DcControllerState,
]

type DhwMessaging = ControlMessaging[
    DhwSensorValues,
    DhwControlValues,
    DhwParameters,
    DhwControlMode,
    DhwControllerState,
]


@strawberry.experimental.pydantic.type(
    model=Stamped,
    all_fields=True,
    use_pydantic_alias=False,
)
class StampedType[T]:
    pass


def get_members(module):
    names = module.__all__ if hasattr(module, "__all__") else dir(module)
    return {name: getattr(module, name) for name in names}


def convert_module(module, class_name_prefix: str):
    for name, cls in get_members(module).items():
        if isclass(cls) and issubclass(cls, ThrsValues):
            gql_cls = type(f"{class_name_prefix}{name}Type", (object,), {})
            strawberry.experimental.pydantic.type(
                model=cls,
                all_fields=True,
                use_pydantic_alias=False,
            )(gql_cls)


convert_module(sensor, "Sensor")
convert_module(control, "Control")
convert_module(controllers, "Controller")
convert_module(simulation, "Simulation")
convert_module(system, "System")


@strawberry.experimental.pydantic.type(
    model=SwitchingControlMode,
    use_pydantic_alias=False,
)
class SwitchingControlModeType[Mode]:
    automatic_mode: Mode | None

    @strawberry.field
    def automatic(self) -> bool:
        return self.automatic_mode is not None


@strawberry.type
class ControlModule[
    SensorValuesType,
    ControlValuesType,
    ParametersType,
    Mode,
    ControllerStateType,
]:
    sensor_values: SensorValuesType | None
    control_values: ControlValuesType | None
    parameters: ParametersType | None
    control_mode: SwitchingControlModeType[Mode] | None = None  # type: ignore
    controller_state: ControllerStateType | None


@dataclass
class ThrsContext(BaseContext):
    messaging: DirectiveMessaging
    thrusters_messaging: ThrustersMessaging
    pvt_messaging: PvtMessaging
    pcm_messaging: PcmMessaging
    adsorption_messaging: AdsorptionMessaging
    consumers_messaging: ConsumersMessaging
    dc_messaging: DcMessaging
    dhw_messaging: DhwMessaging
    drives_messaging: DrivesMessaging
    simulation_messaging: SimulationMessaging


type FieldMutation[T] = """Callable[
    [object, object, strawberry.Info[ThrsContext]],
    Coroutine[None, None, T],
]"""


def generate_mutation_for_field[T](
    cls: type[T],
    name: str,
    field_name: str,
    field: FieldInfo,
    make_fn_key: str,
    messaging: "Callable[[ThrsContext], ControlMessaging | SimulationMessaging]",
    *args,
    unstamp: bool,
) -> "FieldMutation[T]":
    input_type = ensure_input_type(field.annotation, unstamp=unstamp)

    def _make_mutation(name: str, component_type: type):
        async def _mutation(
            self,
            value: component_type,  # type: ignore
            info: "strawberry.Info[ThrsContext]",
        ) -> cls:  # type: ignore
            mod = messaging(info.context)
            value = value.to_pydantic().to_stamped() if unstamp else value
            result = await getattr(mod, make_fn_key)(name, value)
            return cls.from_pydantic(result)  # type: ignore

        return _mutation

    mutation = _make_mutation(field_name, input_type)
    mutation.__name__ = name
    return mutation


def add_control_mutations(
    module: str,
    control_values_cls: type[ThrsValues],
    strawberry_cls: type,
    messaging: "Callable[[ThrsContext], ControlMessaging]",
):
    def _do(cls):
        for name, field in control_values_cls.model_fields.items():
            fn = generate_mutation_for_field(
                strawberry_cls,
                f"{module}_control_set_{name}",
                name,
                field,
                "set_manual_control",
                messaging,
                unstamp=True,
            )
            method = strawberry.mutation(fn)
            setattr(cls, fn.__name__, method)

        return cls

    return _do


def add_parameter_mutations(
    module: str,
    parameters_cls: type[ThrsValues],
    strawberry_cls: type,
    messaging: "Callable[[ThrsContext], ControlMessaging]",
):
    def _do(cls):
        for name, field in parameters_cls.model_fields.items():
            fn = generate_mutation_for_field(
                strawberry_cls,
                f"{module}_parameter_set_{name}",
                name,
                field,
                "set_parameter",
                messaging,
                unstamp=False,
            )
            method = strawberry.mutation(fn)
            setattr(cls, fn.__name__, method)

        return cls

    return _do


def add_simulation_input_mutations(
    mode: str,
    io_mapping: dict[str, tuple[type[ThrsValues], type[ThrsValues]]],
    inputs_strawberry_type_mapping: dict[str, type],
    messaging: "Callable[[ThrsContext], SimulationMessaging]",
):
    strawberry_cls = inputs_strawberry_type_mapping[mode]
    inputs_cls = io_mapping[mode][0]

    def _do(cls):
        for name, field in inputs_cls.model_fields.items():
            fn = generate_mutation_for_field(
                strawberry_cls,
                f"{mode}_simulation_set_{name}",
                name,
                field,
                "set_simulation_input",
                messaging,
                unstamp=True,
            )
            method = strawberry.mutation(fn)
            setattr(cls, fn.__name__, method)

        return cls

    return _do


def add_automation_mode_mutation(
    module: str,
    messaging: "Callable[[ThrsContext], ControlMessaging]",
):
    def _do(cls):
        async def set_automation_mode(
            self,
            automatic: bool,
            info: "strawberry.Info[ThrsContext]",
        ) -> bool:
            mod = messaging(info.context)
            return await mod.set_automation_mode(automatic)

        mutation = strawberry.mutation(set_automation_mode)
        setattr(cls, f"{module}_set_automation_mode", mutation)
        return cls

    return _do


def resolve_module(
    module: ControlMessaging,
) -> ControlModule:
    return ControlModule(
        sensor_values=optional_pydantic_to_graphql(module.sensor_values),
        control_values=optional_pydantic_to_graphql(module.control_values),
        parameters=optional_pydantic_to_graphql(module.parameters),
        control_mode=SwitchingControlModeType.from_pydantic(module.control_mode)
        if module.control_mode
        else None,
        controller_state=optional_pydantic_to_graphql(module.controller_state),
    )
