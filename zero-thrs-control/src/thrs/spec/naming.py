"""How the THRS control API names things in GraphQL.

The API's schema is generated from the pydantic models; these are the rules
that generation follows, stated once so the published contract
(``thrs.spec``) names every field, type, input and mutation exactly as the
API serves it without introspecting the API. ``tests/spec`` checks the two
against each other for as long as both exist.
"""

from enum import Enum
from types import ModuleType

from thrs.input_output.base import ThrsValues
from thrs.input_output.definitions import (
    control,
    controllers,
    sensor,
    simulation,
    system,
)

# The shared component definitions get a type per exported class, prefixed
# by the module it is defined in (`control.Pump` -> `ControlPumpType`).
DEFINITION_PREFIXES: dict[ModuleType, str] = {
    sensor: "Sensor",
    control: "Control",
    controllers: "Controller",
    simulation: "Simulation",
    system: "System",
}

TYPE_SUFFIX = "Type"
INPUT_TYPE_SUFFIX = "InputType"


def field_name(python_name: str) -> str:
    """The GraphQL name of a python field, argument or mutation: lowerCamelCase
    of its snake_case name (``sensor_values`` -> ``sensorValues``)."""
    head, *rest = python_name.split("_")
    return head + "".join(word.capitalize() if word else "_" for word in rest)


def registered_model(cls: type[ThrsValues]) -> type[ThrsValues]:
    """The model a component's GraphQL type is generated from: the class
    itself when its definitions module exports it (or when it is no shared
    definition at all), else the nearest exported base. An unexported subclass
    (``PropulsionDrive(HeatSource)``) is served as its base's type."""
    for base in cls.__mro__:
        module = _definitions_module(base)
        if module is None:
            continue
        if base.__name__ in getattr(module, "__all__", ()):
            return base
    return cls


def type_name(cls: type[ThrsValues]) -> str:
    """The GraphQL object type of a model: ``<Class>Type``, prefixed by its
    definitions module for a shared component (``ControlPumpType``)."""
    model = registered_model(cls)
    module = _definitions_module(model)
    prefix = DEFINITION_PREFIXES[module] if module is not None else ""
    return f"{prefix}{model.__name__}{TYPE_SUFFIX}"


def input_type_name(component_cls: type[ThrsValues]) -> str:
    """The GraphQL input type a component mutation takes: the unstamped
    component, named after the component class itself (``PumpInputType``).
    Two components sharing a class name share the input type."""
    return f"{component_cls.__name__}{INPUT_TYPE_SUFFIX}"


def enum_type_name(enum_cls: type[Enum]) -> str:
    """The GraphQL enum of a python Enum: its class name."""
    return enum_cls.__name__


def generic_type_name(generic: str, *arguments: str) -> str:
    """The name of a specialised generic type: the argument type names joined,
    then the generic's name (``FloatStampedType``, ``<...>ControlModule``)."""
    return "".join(arguments) + generic


def _control_module_arguments(
    sensor_values_cls: type[ThrsValues],
    control_values_cls: type[ThrsValues],
    parameters_cls: type[ThrsValues],
    control_mode_cls: type[ThrsValues],
    controller_state_cls: type[ThrsValues],
) -> tuple[str, ...]:
    return (
        type_name(sensor_values_cls),
        type_name(control_values_cls),
        type_name(parameters_cls),
        type_name(control_mode_cls),
        type_name(controller_state_cls),
    )


def control_module_type_name(
    sensor_values_cls: type[ThrsValues],
    control_values_cls: type[ThrsValues],
    parameters_cls: type[ThrsValues],
    control_mode_cls: type[ThrsValues],
    controller_state_cls: type[ThrsValues],
) -> str:
    """The type of one member of the ``modules`` query: the generic
    ``ControlModule`` specialised by the module's five section types."""
    return generic_type_name(
        "ControlModule",
        *_control_module_arguments(
            sensor_values_cls,
            control_values_cls,
            parameters_cls,
            control_mode_cls,
            controller_state_cls,
        ),
    )


def switching_control_mode_type_name(
    sensor_values_cls: type[ThrsValues],
    control_values_cls: type[ThrsValues],
    parameters_cls: type[ThrsValues],
    control_mode_cls: type[ThrsValues],
    controller_state_cls: type[ThrsValues],
) -> str:
    """The type of a module's ``controlMode`` section. It is the generic
    ``SwitchingControlModeType[Mode]`` nested in ``ControlModule``, and a
    generic nested in another is specialised (and so named) by the outer
    generic's full argument list, not by its own one argument."""
    return generic_type_name(
        "SwitchingControlModeType",
        *_control_module_arguments(
            sensor_values_cls,
            control_values_cls,
            parameters_cls,
            control_mode_cls,
            controller_state_cls,
        ),
    )


def _definitions_module(cls: type) -> ModuleType | None:
    return next(
        (module for module in DEFINITION_PREFIXES if cls.__module__ == module.__name__),
        None,
    )
