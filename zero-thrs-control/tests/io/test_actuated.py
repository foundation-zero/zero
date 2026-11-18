import struct
from datetime import UTC, datetime

from thrs.input_output.actuated import actuated_as_commanded
from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.control import Pump, Valve
from thrs.input_output.definitions.units import PumpControlMode

COMMANDED_AT = datetime(2026, 11, 18, 12, 0, 0, tzinfo=UTC)
ACTUATED_AT = datetime(2026, 11, 18, 12, 0, 7, tzinfo=UTC)


class Values(ThrsValues):
    pump: Pump
    valve: Valve


def values(
    at: datetime,
    dutypoint: float = 0.3,
    on: bool = True,
    control_mode: PumpControlMode | None = PumpControlMode.CONSTANT_SPEED,
    setpoint: float = 0.5,
) -> Values:
    return Values(
        pump=Pump(
            dutypoint=Stamped(value=dutypoint, timestamp=at),
            on=Stamped(value=on, timestamp=at),
            control_mode=Stamped(value=control_mode, timestamp=at),
        ),
        valve=Valve(setpoint=Stamped(value=setpoint, timestamp=at)),
    )


def float32(value: float) -> float:
    return struct.unpack("f", struct.pack("f", value))[0]


def test_a_float_rounded_to_float32_takes_the_command():
    actuated = values(ACTUATED_AT, dutypoint=float32(0.3))
    commanded = values(COMMANDED_AT, dutypoint=0.3)

    published = actuated_as_commanded(actuated, commanded)

    assert published.pump.dutypoint == Stamped(value=0.3, timestamp=COMMANDED_AT)


def test_a_float_that_differs_keeps_the_actuated_value_and_stamp():
    actuated = values(ACTUATED_AT, setpoint=0.49)
    commanded = values(COMMANDED_AT, setpoint=0.5)

    published = actuated_as_commanded(actuated, commanded)

    assert published.valve.setpoint == Stamped(value=0.49, timestamp=ACTUATED_AT)


def test_a_float_more_than_float32_rounding_off_keeps_the_actuated_value():
    actuated = values(ACTUATED_AT, setpoint=0.5 + 1e-6)
    commanded = values(COMMANDED_AT, setpoint=0.5)

    published = actuated_as_commanded(actuated, commanded)

    assert published.valve.setpoint == Stamped(value=0.5 + 1e-6, timestamp=ACTUATED_AT)


def test_a_bool_takes_the_command_only_when_equal():
    same = actuated_as_commanded(
        values(ACTUATED_AT, on=True), values(COMMANDED_AT, on=True)
    )
    differs = actuated_as_commanded(
        values(ACTUATED_AT, on=False), values(COMMANDED_AT, on=True)
    )

    assert same.pump.on == Stamped(value=True, timestamp=COMMANDED_AT)
    assert differs.pump.on == Stamped(value=False, timestamp=ACTUATED_AT)


def test_an_enum_takes_the_command_only_when_equal():
    same = actuated_as_commanded(
        values(ACTUATED_AT, control_mode=PumpControlMode.CONSTANT_SPEED),
        values(COMMANDED_AT, control_mode=PumpControlMode.CONSTANT_SPEED),
    )
    differs = actuated_as_commanded(
        values(ACTUATED_AT, control_mode=PumpControlMode.CONSTANT_PRESSURE),
        values(COMMANDED_AT, control_mode=PumpControlMode.CONSTANT_SPEED),
    )

    assert same.pump.control_mode.timestamp == COMMANDED_AT
    assert differs.pump.control_mode == Stamped(
        value=PumpControlMode.CONSTANT_PRESSURE.value, timestamp=ACTUATED_AT
    )


def test_a_missing_value_never_matches():
    actuated = values(ACTUATED_AT, control_mode=None)
    commanded = values(COMMANDED_AT, control_mode=None)

    published = actuated_as_commanded(actuated, commanded)

    assert published.pump.control_mode == Stamped(value=None, timestamp=ACTUATED_AT)


def test_list_items_are_matched_by_position():
    class Switches(ThrsValues):
        switches: list[Valve]

    def switches(at: datetime, *setpoints: float) -> Switches:
        return Switches(
            switches=[
                Valve(setpoint=Stamped(value=setpoint, timestamp=at))
                for setpoint in setpoints
            ]
        )

    actuated = switches(ACTUATED_AT, float32(0.3), 0.7)
    commanded = switches(COMMANDED_AT, 0.3, 0.6)
    actuated_before = actuated.model_copy(deep=True)

    published = actuated_as_commanded(actuated, commanded)

    assert [switch.setpoint for switch in published.switches] == [
        Stamped(value=0.3, timestamp=COMMANDED_AT),
        Stamped(value=0.7, timestamp=ACTUATED_AT),
    ]
    assert actuated == actuated_before


def test_neither_argument_is_modified():
    actuated = values(ACTUATED_AT, dutypoint=float32(0.3))
    commanded = values(COMMANDED_AT, dutypoint=0.3)
    actuated_before = actuated.model_copy(deep=True)
    commanded_before = commanded.model_copy(deep=True)

    actuated_as_commanded(actuated, commanded)

    assert actuated == actuated_before
    assert commanded == commanded_before
