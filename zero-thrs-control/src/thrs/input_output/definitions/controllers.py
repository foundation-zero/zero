from enum import Enum

from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.units import (
    Celsius,
    DeltaT,
    Joule,
    Liter,
    LMin,
    OptionalJoule,
    OptionalRatio,
    Ratio,
    Seconds,
    TankState,
    Watt,
)


class PcmChargingState(Enum):
    IDLE = "idle"
    CHARGING = "charging"
    DISCHARGING = "discharging"


class PcmChargeStatus(Enum):
    UNKNOWN = "unknown"
    EMPTY = "empty"
    INTERMEDIATE = "intermediate"
    FULL = "full"


PCM_CHARGING_DEADBAND: Watt = 100
PCM_MIN_FLOW: LMin = 0.5  # below this the dT across a module is noise
# Must exceed the 60 s MQTT republish interval of unchanged values.
PCM_MAX_SAMPLE_GAP: Seconds = 90

PCM_MELT_TEMP: Celsius = 58
PCM_MELT_MARGIN: DeltaT = (
    3  # inlet must be this far past PCM_MELT_TEMP to define EMPTY/FULL
)

# Exchanger effectiveness dT / (T_in - PCM_MELT_TEMP) below which a module is exhausted.
# TODO: Fit on logged full charge/discharge cycles.
PCM_EXHAUSTED_EFFECTIVENESS: Ratio = 0.2
PCM_ANCHOR_DWELL: Seconds = 300

# TODO: Replace with a figure measured over a full charge/discharge cycle. Roughly the latent heat of 110 kg PCM58
PCM_MODULE_CAPACITY: Joule = 7 * 3.6e6

PCM_STANDBY_LOSS: Watt = 32.1  # 0.77 kWh/24h
PCM_HEATING_ELEMENT_POWER: Watt = 2800

# Below this, net measured heat since an anchor is noise, not evidence of leaving it.
PCM_STATUS_DEADBAND: Joule = 0.1 * 3.6e6  # 0.1 kWh

# Exchanger water contents, named by the port labels. Pipe runs not included.
PCM_EXCHANGER_BC_VOLUME: Liter = 3.5
PCM_EXCHANGER_AD_VOLUME: Liter = 6.8

PCM_MODULE1_PURGE_VOLUME: Liter = PCM_EXCHANGER_BC_VOLUME
PCM_MODULE1_FRESHWATER_PURGE_VOLUME: Liter = PCM_EXCHANGER_AD_VOLUME
PCM_MODULE_PURGE_VOLUME: Liter = PCM_EXCHANGER_BC_VOLUME + PCM_EXCHANGER_AD_VOLUME


class PidControllerValues(
    ThrsValues
):  # Not using generics here for strawberry compatibility.
    setpoint: Stamped[float]
    measurement: Stamped[float | None]
    output: Stamped[float | None]
    error: Stamped[float | None]
    enabled: Stamped[bool]
    tuning: Stamped[tuple[float, float, float]]
    components: Stamped[tuple[float, float, float]]


class TanksControllerValues(ThrsValues):
    tank1_state: Stamped[TankState]
    tank2_state: Stamped[TankState]
    tank3_state: Stamped[TankState]
    time_to_fill: Stamped[Seconds | None]
    time_to_hot: Stamped[Seconds | None]


class PcmChargeControllerValues(ThrsValues):
    charge: Stamped[OptionalRatio]
    energy: Stamped[OptionalJoule]
    charge_status: Stamped[PcmChargeStatus]
    charging_state: Stamped[PcmChargingState]


__all__ = [
    "PcmChargeControllerValues",
    "PcmChargeStatus",
    "PidControllerValues",
    "TanksControllerValues",
]
