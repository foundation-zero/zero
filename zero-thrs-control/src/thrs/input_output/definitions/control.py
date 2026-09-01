from datetime import UTC, datetime
from typing import Annotated, Any, ClassVar

from pydantic import field_validator, model_serializer, model_validator

from thrs.input_output.base import Stamped, ThrsValues, field_meta
from thrs.input_output.definitions.units import (
    AdsorptionChillerMode,
    Celsius,
    DeltaT,
    FreeCoolingMode,
    OnOff,
    Ratio,
    TankControlMode,
)
from thrs.input_output.definitions.wire_context import is_actuated, is_commanded


class Pump(ThrsValues):
    @model_validator(mode="wrap")
    @classmethod
    def _read_actuated(cls, values: Any, handler, info):
        if not isinstance(values, dict):
            return handler(values)

        if is_actuated(info.context):
            for field, actuated_key in (
                ("Dutypoint", "CC_Dutypoint"),
                ("On", "CC_OnOff"),
                ("ControlMode", "CC_ControlMode"),
            ):
                if actuated_key in values:
                    values[field] = values.pop(actuated_key)
                elif field in values:
                    values.pop(field)
        elif is_commanded(info.context) and any(
            key in values for key in ("CC_Dutypoint", "CC_OnOff", "CC_ControlMode")
        ):
            raise ValueError("CC_ keys are not valid for commanded values")

        return handler(values)

    @model_serializer(mode="wrap")
    def _write_actuated(self, handler, info):
        data = handler(self)
        if is_actuated(info.context):
            for key, actuated_key in (
                ("Dutypoint", "CC_Dutypoint"),
                ("On", "CC_OnOff"),
                ("ControlMode", "CC_ControlMode"),
            ):
                if key in data:
                    value = data.pop(key)
                    if value["Value"] is not None:
                        data[actuated_key] = value
        return data

    dutypoint: Stamped[Ratio]
    on: Stamped[OnOff]
    control_mode: Annotated[Stamped[int | None], field_meta(included_in_fmu=False)] = (
        Stamped(value=None, timestamp=datetime.fromtimestamp(0, UTC))
    )

    # TODO: Remove once marpower fixes this on their side
    @field_validator("dutypoint")
    @classmethod
    def correct_marpower_range(cls, value: Stamped[Ratio]) -> Stamped[Ratio]:
        if value.value > 1.0:
            value.value /= 100

        return value


class Valve(ThrsValues):
    CLOSED: ClassVar = 0.0
    OPEN: ClassVar = 1.0

    SWITCH_B: ClassVar = 0.0
    SWITCH_A: ClassVar = 1.0

    MIXING_B_TO_AB: ClassVar = 0.0
    MIXING_A_TO_AB: ClassVar = 1.0

    setpoint: Stamped[Ratio]
    """
    The setpoint of the valve, represented as a ratio between 0 and 1.

    Valve Conventions:
        - 2-Way Switch or Flow Control Valve:
            - 0: Closed
            - 1: Open
        - 3-Way Switch Valve:
            - 0: Flow from AB to B
            - 1: Flow from AB to A
        - Mixing Valve:
            - 0: Flow from B to AB
            - 1: Flow from A to AB
    """

    @model_validator(mode="wrap")
    @classmethod
    def _read_actuated(cls, values: Any, handler, info):
        if not isinstance(values, dict):
            return handler(values)

        if is_actuated(info.context):
            if "CC_Setpoint" in values:
                values["Setpoint"] = values.pop("CC_Setpoint")
            elif "Setpoint" in values:
                # Remove plain Setpoint when reading actuated (it's the setpoint request, not the actual setpoint)
                values.pop("Setpoint")
        elif is_commanded(info.context) and "CC_Setpoint" in values:
            # Actuated keys belong to the AMCS receive flow, not to commands.
            raise ValueError("CC_Setpoint is not valid for commanded values")

        return handler(values)

    @model_serializer(mode="wrap")
    def _write_actuated(self, handler, info):
        data = handler(self)
        if is_actuated(info.context):
            for key in ("Setpoint", "setpoint"):
                if key in data:
                    data["CC_Setpoint"] = data.pop(key)
                    break
        return data

    # TODO: Remove once marpower fixes this on their side
    @field_validator("setpoint")
    @classmethod
    def correct_marpower_range(cls, value: Stamped[Ratio]) -> Stamped[Ratio]:
        if value.value > 1.0:
            value.value /= 100

        return value


class Pcm(ThrsValues):
    on: Stamped[OnOff]


class AdsorptionChiller(ThrsValues):
    enable: Stamped[OnOff]
    mode: Stamped[AdsorptionChillerMode]
    cooling_setpoint: Stamped[Celsius]
    free_cooling_mode: Annotated[
        Stamped[FreeCoolingMode], field_meta(included_in_fmu=False)
    ]
    available_seawater_temperature: Annotated[
        Stamped[Celsius], field_meta(included_in_fmu=False)
    ]
    available_hot_temperature: Stamped[Celsius]
    available_cold_temperature: Stamped[Celsius]
    cold_minimum: Stamped[Celsius]
    hot_minimum: Stamped[Celsius]
    cold_hysteresis: Stamped[DeltaT]
    hot_hysteresis: Stamped[DeltaT]
    tank_control_mode: Annotated[
        Stamped[TankControlMode], field_meta(included_in_fmu=False)
    ]


class HeatPump(ThrsValues):
    on: Stamped[OnOff]
    temperature_setpoint: Stamped[Celsius]


__all__ = ["AdsorptionChiller", "HeatPump", "Pcm", "Pump", "Valve"]
