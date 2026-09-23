from enum import Enum

from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.units import (
    Celsius,
    Charged,
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


PCM_CHARGING_DEADBAND: Watt = 100
PCM_MIN_FLOW: LMin = 0.5  # below this the measured dT across a module is noise
PCM_MAX_SAMPLE_GAP: Seconds = 30  # never integrate across a longer dropout

# PCM58 has a phase transition at 58 C (Flamco FlexTherm Eco manual, ch. 1). Nothing
# can be concluded about the phase fraction unless the inlet is clearly past it.
PCM_MELT_TEMP: Celsius = 58
PCM_MELT_MARGIN: DeltaT = 3

# The outlet converging on the inlet means the module has stopped exchanging heat, so
# there is no phase change left to drive. This, not any absolute outlet temperature,
# is what says a module is full or empty: the datasheet quotes a 50-55 C outlet during
# normal discharge, which reflects the exchanger approach, not the state of charge.
PCM_EXHAUSTED_DT: DeltaT = 1.5
PCM_ANCHOR_DWELL: Seconds = 300

# TODO: Replace with a figure measured over a full charge/discharge cycle. This is NOT
# the 10.5 kWh nameplate: that rates the tapwater deliverable between a 75 C charge and
# a 10 -> 40 C draw-off, whereas we charge to ~65-70 C and discharge into a loop
# returning around 50 C, so what is actually usable is roughly the latent plateau of
# the 110 kg of PCM58.
PCM_MODULE_CAPACITY: Joule = 7 * 3.6e6

# Standing loss per module, FlexTherm Eco 9E: 0.77 kWh/24h (manual, table 2.2).
PCM_STANDBY_LOSS: Watt = 32.1

# The electric element, 2.8 kW at 230 V (manual, table 2.2). Only module 1 has one
# connected. It heats the cell directly, so none of it shows up in the water, which is
# why the balance has to be told when it is switched on. The unit's own thermostat can
# cut the element out while our output stays closed, so this over-counts when it does.
PCM_HEATING_ELEMENT_POWER: Watt = 2800

# The pipework and exchangers read stale without flow, so a circuit has to be purged
# before its dT means anything. Water contents per exchanger, 9E (manual, table 2.2);
# the pipe runs to and from the module are not included yet.
PCM_LPC_VOLUME: Liter = 3.5
PCM_HPC_VOLUME: Liter = 6.8

# Module 1 gives the thrs loop its LPC and the freshwater system its HPC. Modules 2-4
# run both exchangers in parallel on the thrs loop, so theirs is one combined circuit.
PCM_MODULE1_PURGE_VOLUME: Liter = PCM_LPC_VOLUME
PCM_MODULE1_FRESHWATER_PURGE_VOLUME: Liter = PCM_HPC_VOLUME
PCM_MODULE_PURGE_VOLUME: Liter = PCM_LPC_VOLUME + PCM_HPC_VOLUME

PCM_CHARGED_THRESHOLD: Ratio = 0.15


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
    # None until an end point has been observed: the integral has no absolute reference
    # before that, and a fabricated 0.5 would be indistinguishable from a measurement.
    charge: Stamped[OptionalRatio]
    # Logged alongside the ratio so a corrected capacity can be applied retrospectively.
    energy: Stamped[OptionalJoule]
    charged: Stamped[Charged]
    charging_state: Stamped[PcmChargingState]


__all__ = [
    "PcmChargeControllerValues",
    "PidControllerValues",
    "TanksControllerValues",
]
