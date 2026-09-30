"""How the THRS control API names things in GraphQL, so the spec matches without introspection."""

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

# `control.Pump` -> `ControlPumpType`.
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
    """The lowerCamelCase GraphQL name of a snake_case python name."""
    head, *rest = python_name.split("_")
    return head + "".join(word.capitalize() if word else "_" for word in rest)


def registered_model(cls: type[ThrsValues]) -> type[ThrsValues]:
    """The class, or its nearest base exported by a definitions module.

    An unexported subclass (``PropulsionDrive(HeatSource)``) is served as its base's type.
    """
    for base in cls.__mro__:
        module = _definitions_module(base)
        if module is None:
            continue
        if base.__name__ in getattr(module, "__all__", ()):
            return base
    return cls


def type_name(cls: type[ThrsValues]) -> str:
    """The GraphQL object type of a model (``ControlPumpType``)."""
    model = registered_model(cls)
    module = _definitions_module(model)
    prefix = DEFINITION_PREFIXES[module] if module is not None else ""
    return f"{prefix}{model.__name__}{TYPE_SUFFIX}"


def input_type_name(component_cls: type[ThrsValues]) -> str:
    """The GraphQL input type of a component mutation; shared by same-named classes."""
    return f"{component_cls.__name__}{INPUT_TYPE_SUFFIX}"


def enum_type_name(enum_cls: type[Enum]) -> str:
    """The GraphQL enum of a python Enum: its class name."""
    return enum_cls.__name__


def generic_type_name(generic: str, *arguments: str) -> str:
    """The name of a specialised generic type (``FloatStampedType``)."""
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
    """The type of one member of the ``modules`` query."""
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
    """The type of a module's ``controlMode`` section.

    As a generic nested in ``ControlModule``, it is named by the outer generic's arguments.
    """
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
