"""The AMCS integer fields whose values stand for named modes.

The IO list gives these fields only a data type, so their meaning is kept
here, per field name; each name belongs to one component type. The names
follow THRS control (`ControlMode` and `PumpControlMode` in
zero-thrs-control).
"""

from enum import IntEnum


class AmcsControlMode(IntEnum):
    LOCAL = 0
    MANUAL = 1
    AUTO = 2
    EXTERNAL = 3


class PumpControlMode(IntEnum):
    """The Wilo `controlFunction` register (holding register 42), from the Wilo
    Modbus datapoint list. THRS control sets only 1, 3 and 4; the others are
    the generic modes a pump can also be set to on site, so that reading one
    back is not an unknown value.
    """

    CONSTANT_SPEED = 1
    CONSTANT_DIFFERENTIAL_PRESSURE = 3
    VARIABLE_DIFFERENTIAL_PRESSURE = 4
    CONSTANT_PRESSURE = 5
    CONSTANT_TEMPERATURE = 9
    CONSTANT_DIFFERENTIAL_TEMPERATURE = 10
    INVALID = 15


ENUMS: dict[str, type[IntEnum]] = {
    "Mode": AmcsControlMode,  # ComponentType.AMCS_MODE
    "CC_ControlMode": PumpControlMode,  # ComponentType.PUMP
}
