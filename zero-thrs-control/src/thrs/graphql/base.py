from dataclasses import dataclass
from inspect import isclass
from typing import Callable, Coroutine

import strawberry
from pydantic.fields import FieldInfo
from strawberry.fastapi import BaseContext

import thrs.input_output.definitions.control as control
import thrs.input_output.definitions.controllers as controllers
import thrs.input_output.definitions.sensor as sensor
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
from thrs.graphql.helpers import (
    JsonSchemaDirective,
    ensure_input_type,
    optional_pydantic_to_graphql,
)
from thrs.graphql.messaging import ControlMessaging, Messaging, SimulationMessaging
from thrs.input_output.base import SimulationInputs, Stamped, ThrsValues
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
    json_schema_directive=JsonSchemaDirective,
    use_pydantic_alias=False,
)
class StampedType[T]:
    pass


def get_members(module):
    if hasattr(module, "__all__"):
        names = module.__all__
    else:
        names = dir(module)
    return {name: getattr(module, name) for name in names}


def convert_module(module, class_name_prefix: str):
    for name, cls in get_members(module).items():
        if isclass(cls) and issubclass(cls, ThrsValues):
            gql_cls = type(f"{class_name_prefix}{name}Type", (object,), {})
            strawberry.experimental.pydantic.type(
                model=cls,
                all_fields=True,
                json_schema_directive=JsonSchemaDirective,
                use_pydantic_alias=False,
            )(gql_cls)


convert_module(sensor, "Sensor")
convert_module(control, "Control")
convert_module(controllers, "Controller")


# TODO: check if this can't just be based on the pydantic model directly
@strawberry.type
class SwitchingControlModeType[Mode]:
    automatic_mode: Mode | None

    @classmethod
    def from_pydantic(
        cls, type, mode: SwitchingControlMode[Mode]
    ) -> "SwitchingControlModeType[Mode]":
        return cls(
            automatic_mode=optional_pydantic_to_graphql(type, mode.automatic_mode)
        )

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
    messaging: Messaging
    thrusters_messaging: ThrustersMessaging
    pvt_messaging: PvtMessaging
    pcm_messaging: PcmMessaging
    consumers_messaging: ConsumersMessaging
    dhw_messaging: DhwMessaging
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
    make_fn: "Callable[[str, type], FieldMutation[T]]",
    *args,
    unstamp: bool,
) -> "FieldMutation[T]":
    input_type = ensure_input_type(field.annotation, unstamp=unstamp)
    mutation = make_fn(field_name, input_type)
    mutation.__name__ = name
    return mutation


def add_control_mutations(
    module: str,
    control_values_cls: type[ThrsValues],
    strawberry_cls: type,
    messaging: Callable[[ThrsContext], ControlMessaging],
):
    def _do(cls):
        def _make_control_mutation(name: str, component_type: type):
            async def _mutation(
                self,
                component: component_type,  # type: ignore
                info: strawberry.Info[ThrsContext],
            ) -> strawberry_cls:  # type: ignore
                mod = messaging(info.context)
                control_values = mod.control_values
                if control_values is None:
                    raise Exception("No control values available to modify")
                pydantic_value = component.to_pydantic().to_stamped()
                setattr(control_values, name, pydantic_value)
                expect = mod.wait_for_control_values(
                    lambda v: getattr(v, name) == pydantic_value, timeout=2.0
                )
                await mod.send_manual_controls(control_values)
                await expect
                return strawberry_cls.from_pydantic(control_values)

            return _mutation

        for name, field in control_values_cls.model_fields.items():
            fn = generate_mutation_for_field(
                strawberry_cls,
                f"{module}_control_set_{name}",
                name,
                field,
                _make_control_mutation,
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
    messaging: Callable[[ThrsContext], ControlMessaging],
):
    def _do(cls):
        def _make_parameter_mutation(name: str, component_type: type):
            async def _mutation(
                self,
                value: component_type,  # type: ignore
                info: strawberry.Info[ThrsContext],
            ) -> strawberry_cls:  # type: ignore
                mod = messaging(info.context)
                parameters = mod.parameters
                if parameters is None:
                    raise Exception("No parameters available to update")
                setattr(parameters, name, value)
                expect = mod.wait_for_controller_state(
                    lambda parameters: getattr(parameters, name) == value, timeout=2
                )
                await mod.set_parameters(parameters)
                await expect
                return strawberry_cls.from_pydantic(parameters)

            return _mutation

        for name, field in parameters_cls.model_fields.items():
            fn = generate_mutation_for_field(
                strawberry_cls,
                f"{module}_parameter_set_{name}",
                name,
                field,
                _make_parameter_mutation,
                unstamp=False,
            )
            method = strawberry.mutation(fn)
            setattr(cls, fn.__name__, method)

        return cls

    return _do


def add_simulation_input_mutations(
    mode: str,
    io_mapping: dict[str, tuple[type[SimulationInputs], type[ThrsValues]]],
    inputs_strawberry_type_mapping: dict[str, type],
    messaging: Callable[[ThrsContext], SimulationMessaging],
):
    strawberry_cls = inputs_strawberry_type_mapping[mode]
    inputs_cls = io_mapping[mode][0]

    def _do(cls):
        def _make_simulation_input_mutation(name: str, component_type: type):
            async def _mutation(
                self,
                component: component_type,  # type: ignore
                info: strawberry.Info[ThrsContext],
            ) -> strawberry_cls:  # type: ignore
                mod = messaging(info.context)
                inputs = mod.simulation_inputs
                if inputs is None:
                    raise Exception("No simulation inputs available to modify")
                pydantic_value = component.to_pydantic().to_stamped()
                setattr(inputs, name, pydantic_value)

                expect = mod.wait_for_simulation_inputs(
                    lambda inputs: getattr(inputs, name) == pydantic_value,
                    timeout=2,
                )
                await mod.set_simulation_inputs(inputs)
                await expect
                return strawberry_cls.from_pydantic(inputs)

            return _mutation

        for name, field in inputs_cls.model_fields.items():
            fn = generate_mutation_for_field(
                strawberry_cls,
                f"{mode}_simulation_set_{name}",
                name,
                field,
                _make_simulation_input_mutation,
                unstamp=True,
            )
            method = strawberry.mutation(fn)
            setattr(cls, fn.__name__, method)

        return cls

    return _do


def add_automation_mode_mutation(
    module: str,
    messaging: Callable[[ThrsContext], ControlMessaging],
):
    def _do(cls):
        async def set_automation_mode(
            self,
            automatic: bool,
            info: strawberry.Info[ThrsContext],
        ) -> bool:
            mod = messaging(info.context)
            await mod.set_automation_mode(automatic)
            await mod.wait_for_control_mode(automatic, timeout=2)
            return True

        mutation = strawberry.mutation(set_automation_mode)
        setattr(cls, f"{module}_set_automation_mode", mutation)
        return cls

    return _do
