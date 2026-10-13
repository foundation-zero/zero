from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from pytest import approx

from thrs.control.controllers import PcmChargeController
from thrs.input_output.base import Stamped
from thrs.input_output.definitions import sensor
from thrs.input_output.definitions.controllers import (
    PCM_ANCHOR_DWELL,
    PCM_HEATING_ELEMENT_POWER,
    PCM_MODULE1_FRESHWATER_PURGE_VOLUME,
    PCM_MODULE1_PURGE_VOLUME,
    PCM_MODULE_CAPACITY,
    PCM_MODULE_PURGE_VOLUME,
    PCM_STANDBY_LOSS,
    PCM_STATUS_DEADBAND,
    PcmChargeStatus,
    PcmChargingState,
)
from thrs.input_output.definitions.units import (
    GLYCOL_20_HEAT_TRANSFER_CONVERSION,
    Celsius,
    LMin,
)

FLOW: LMin = 5.0
STEP = 10.0  # seconds; well inside the sample gap limit

# Flushes the largest circuit at FLOW, plus a step for the first sample, which only sets
# the clock.
PURGE_SECONDS = 60 * PCM_MODULE_PURGE_VOLUME / FLOW + 2 * STEP
DWELL_SECONDS = PCM_ANCHOR_DWELL + 2 * STEP


class Clock:
    def __init__(self) -> None:
        self.now = datetime(2026, 1, 1, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += timedelta(seconds=seconds)


def _device(
    inlet: Celsius | None, outlet: Celsius, flow: LMin, timestamp: datetime
) -> sensor.HeatTransferDevice:
    return sensor.HeatTransferDevice.from_sensors(
        temperature_supply=Stamped(value=inlet, timestamp=timestamp),
        temperature_return=Stamped(value=outlet, timestamp=timestamp),
        flow=Stamped(value=flow, timestamp=timestamp),
        temperature_supply_source="inlet",
        temperature_return_source="outlet",
        flow_source="flow",
        heat_transfer_conversion=GLYCOL_20_HEAT_TRANSFER_CONVERSION,
    )


def _feed(
    controller: PcmChargeController,
    clock: Clock,
    devices: Callable[[datetime], tuple[sensor.HeatTransferDevice, ...]],
    seconds: float,
    step: float = STEP,
    heating: bool = False,
) -> None:
    for _ in range(round(seconds / step)):
        clock.advance(step)
        controller(*devices(clock.now), heating=heating)


def _single(
    inlet: Celsius | None, outlet: Celsius, flow: LMin = FLOW
) -> Callable[[datetime], tuple[sensor.HeatTransferDevice, ...]]:
    return lambda timestamp: (_device(inlet, outlet, flow, timestamp),)


def _charge(clock: Clock, controller: PcmChargeController, seconds: float) -> None:
    """Hold a full anchor: hot inlet, outlet converged on it."""
    _feed(controller, clock, _single(inlet=70.0, outlet=70.0), seconds)


def _discharge(clock: Clock, controller: PcmChargeController, seconds: float) -> None:
    """Hold an empty anchor: cold inlet, outlet converged on it."""
    _feed(controller, clock, _single(inlet=45.0, outlet=45.0), seconds)


def test_charge_is_unknown_before_any_anchor():
    clock = Clock()
    controller = PcmChargeController(clock)

    _feed(controller, clock, _single(inlet=70.0, outlet=58.0), seconds=3600)

    assert controller.values().charge.value is None
    assert controller.values().energy.value is None


def test_status_is_unknown_before_any_anchor():
    controller = PcmChargeController(Clock())

    assert controller.values().charge_status.value == PcmChargeStatus.UNKNOWN.value


def test_converged_hot_inlet_anchors_full():
    clock = Clock()
    controller = PcmChargeController(clock)

    _charge(clock, controller, PURGE_SECONDS + DWELL_SECONDS)

    assert controller.values().charge.value == approx(1.0)
    assert controller.values().energy.value == approx(PCM_MODULE_CAPACITY)
    assert controller.values().charge_status.value == PcmChargeStatus.FULL.value


def test_converged_cold_inlet_anchors_empty():
    clock = Clock()
    controller = PcmChargeController(clock)

    _discharge(clock, controller, PURGE_SECONDS + DWELL_SECONDS)

    assert controller.values().charge.value == approx(0.0)
    assert controller.values().charge_status.value == PcmChargeStatus.EMPTY.value


def test_no_anchor_before_the_circuit_is_purged():
    """The sensors are in the pipework, so they read stale water until it is flushed."""
    clock = Clock()
    controller = PcmChargeController(clock)

    _charge(clock, controller, PURGE_SECONDS - 3 * STEP)

    assert controller.values().charge.value is None


def test_no_anchor_before_the_dwell_has_elapsed():
    clock = Clock()
    controller = PcmChargeController(clock)

    _charge(clock, controller, PURGE_SECONDS + PCM_ANCHOR_DWELL - 4 * STEP)

    assert controller.values().charge.value is None


def test_outlet_far_from_inlet_does_not_anchor():
    """A module still taking heat has phase change left, whatever its outlet reads."""
    clock = Clock()
    controller = PcmChargeController(clock)

    _feed(
        controller,
        clock,
        _single(inlet=70.0, outlet=62.0),
        seconds=PURGE_SECONDS + DWELL_SECONDS,
    )

    assert controller.values().charge.value is None


def test_discharge_outlet_in_the_manufacturer_band_does_not_anchor_empty():
    """50-55 C out is the exchanger approach, not an empty module."""
    clock = Clock()
    controller = PcmChargeController(clock)

    _charge(clock, controller, PURGE_SECONDS + DWELL_SECONDS)
    _feed(
        controller,
        clock,
        _single(inlet=45.0, outlet=53.0),
        seconds=PURGE_SECONDS + DWELL_SECONDS,
    )

    charge = controller.values().charge.value
    assert charge is not None and charge > 0.0


def test_small_dt_does_not_anchor_with_little_drive():
    """1 K across a module with its inlet 4 K past the melt point is still melting."""
    clock = Clock()
    controller = PcmChargeController(clock)

    _feed(
        controller,
        clock,
        _single(inlet=62.0, outlet=61.0),
        seconds=PURGE_SECONDS + DWELL_SECONDS,
    )

    assert controller.values().charge.value is None


def test_same_dt_anchors_with_a_large_drive():
    clock = Clock()
    controller = PcmChargeController(clock)

    _feed(
        controller,
        clock,
        _single(inlet=75.0, outlet=74.0),
        seconds=PURGE_SECONDS + DWELL_SECONDS,
    )

    assert controller.values().charge.value == approx(1.0)


def test_unknown_inlet_is_not_integrated():
    """Between valve positions the inlet is unknown, and so is the heat."""
    clock = Clock()
    controller = PcmChargeController(clock)

    _discharge(clock, controller, PURGE_SECONDS + DWELL_SECONDS)
    _feed(controller, clock, _single(inlet=None, outlet=60.0), seconds=600)

    assert controller.values().energy.value == approx(0.0)


def test_unknown_inlet_restarts_the_purge():
    clock = Clock()
    controller = PcmChargeController(clock)

    _discharge(clock, controller, PURGE_SECONDS + DWELL_SECONDS)
    _feed(controller, clock, _single(inlet=None, outlet=60.0), seconds=60)
    _feed(controller, clock, _single(inlet=70.0, outlet=60.0), seconds=60)

    assert controller.values().energy.value == approx(0.0)


def test_a_gap_in_the_data_restarts_the_purge():
    clock = Clock()
    controller = PcmChargeController(clock)

    _discharge(clock, controller, PURGE_SECONDS + DWELL_SECONDS)
    _feed(controller, clock, _single(inlet=70.0, outlet=60.0), seconds=600, step=600)
    _feed(controller, clock, _single(inlet=70.0, outlet=60.0), seconds=60)

    assert controller.values().energy.value == approx(0.0)


def test_energy_is_integrated_between_anchors():
    clock = Clock()
    controller = PcmChargeController(clock)

    _discharge(clock, controller, PURGE_SECONDS + DWELL_SECONDS)
    _feed(controller, clock, _single(inlet=70.0, outlet=60.0), seconds=600)

    power = FLOW * 10.0 * GLYCOL_20_HEAT_TRANSFER_CONVERSION
    assert controller.values().energy.value == approx(power * 600)


def test_standby_loss_applies_while_idle():
    clock = Clock()
    controller = PcmChargeController(clock)

    _charge(clock, controller, PURGE_SECONDS + DWELL_SECONDS)
    _feed(controller, clock, _single(inlet=20.0, outlet=20.0, flow=0.0), seconds=3600)

    assert controller.values().energy.value == approx(
        PCM_MODULE_CAPACITY - PCM_STANDBY_LOSS * 3600
    )


def test_a_gap_in_the_data_is_not_integrated():
    clock = Clock()
    controller = PcmChargeController(clock)

    _discharge(clock, controller, PURGE_SECONDS + DWELL_SECONDS)
    _feed(controller, clock, _single(inlet=70.0, outlet=60.0), seconds=600, step=600)

    assert controller.values().energy.value == approx(0.0)


def test_energy_is_clamped_to_capacity():
    clock = Clock()
    controller = PcmChargeController(clock)

    _charge(clock, controller, PURGE_SECONDS + DWELL_SECONDS)
    _feed(controller, clock, _single(inlet=70.0, outlet=60.0), seconds=7200)

    assert controller.values().energy.value == approx(PCM_MODULE_CAPACITY)


def test_freshwater_circuit_discharges_module1():
    """Module 1 can be drawn down over its A-D exchanger with the thrs loop idle."""
    clock = Clock()
    controller = PcmChargeController(
        clock, (PCM_MODULE1_PURGE_VOLUME, PCM_MODULE1_FRESHWATER_PURGE_VOLUME)
    )

    def circuits(timestamp: datetime) -> tuple[sensor.HeatTransferDevice, ...]:
        return (
            _device(inlet=70.0, outlet=70.0, flow=FLOW, timestamp=timestamp),
            _device(inlet=20.0, outlet=20.0, flow=0.0, timestamp=timestamp),
        )

    _feed(controller, clock, circuits, seconds=PURGE_SECONDS + DWELL_SECONDS)
    assert controller.values().charge.value == approx(1.0)

    def freshwater_draw(timestamp: datetime) -> tuple[sensor.HeatTransferDevice, ...]:
        return (
            _device(inlet=70.0, outlet=70.0, flow=0.0, timestamp=timestamp),
            _device(inlet=15.0, outlet=55.0, flow=FLOW, timestamp=timestamp),
        )

    _feed(controller, clock, freshwater_draw, seconds=PURGE_SECONDS + 600)

    charge = controller.values().charge.value
    assert charge is not None and charge < 1.0


def test_heating_element_charges_a_module_with_nothing_flowing():
    """Module 1's element heats the cell directly, so no circuit ever sees it."""
    clock = Clock()
    controller = PcmChargeController(
        clock, heating_power=PCM_HEATING_ELEMENT_POWER, capacity=PCM_MODULE_CAPACITY
    )

    _discharge(clock, controller, PURGE_SECONDS + DWELL_SECONDS)
    _feed(
        controller,
        clock,
        _single(inlet=20.0, outlet=20.0, flow=0.0),
        seconds=600,
        heating=True,
    )

    assert controller.values().energy.value == approx(
        (PCM_HEATING_ELEMENT_POWER - PCM_STANDBY_LOSS) * 600
    )


def test_heating_element_counts_as_charging():
    clock = Clock()
    controller = PcmChargeController(clock, heating_power=PCM_HEATING_ELEMENT_POWER)

    _feed(
        controller,
        clock,
        _single(inlet=20.0, outlet=20.0, flow=0.0),
        seconds=60,
        heating=True,
    )

    assert controller.values().charging_state.value == PcmChargingState.CHARGING.value


def test_heating_element_adds_to_the_hydronic_balance():
    clock = Clock()
    controller = PcmChargeController(
        clock, heating_power=PCM_HEATING_ELEMENT_POWER, capacity=PCM_MODULE_CAPACITY
    )

    _discharge(clock, controller, PURGE_SECONDS + DWELL_SECONDS)
    _feed(
        controller,
        clock,
        _single(inlet=70.0, outlet=60.0),
        seconds=600,
        heating=True,
    )

    water = FLOW * 10.0 * GLYCOL_20_HEAT_TRANSFER_CONVERSION
    assert controller.values().energy.value == approx(
        (water + PCM_HEATING_ELEMENT_POWER) * 600
    )


def test_modules_without_an_element_ignore_the_heating_flag():
    clock = Clock()
    controller = PcmChargeController(clock)  # heating_power defaults to zero

    _discharge(clock, controller, PURGE_SECONDS + DWELL_SECONDS)
    _feed(
        controller,
        clock,
        _single(inlet=20.0, outlet=20.0, flow=0.0),
        seconds=600,
        heating=True,
    )

    assert controller.values().energy.value == approx(0.0)


def test_circuits_that_disagree_do_not_anchor():
    """One circuit reading full while the other reads empty is not evidence of either."""
    clock = Clock()
    controller = PcmChargeController(
        clock, (PCM_MODULE1_PURGE_VOLUME, PCM_MODULE1_FRESHWATER_PURGE_VOLUME)
    )

    def circuits(timestamp: datetime) -> tuple[sensor.HeatTransferDevice, ...]:
        return (
            _device(inlet=70.0, outlet=70.0, flow=FLOW, timestamp=timestamp),
            _device(inlet=45.0, outlet=45.0, flow=FLOW, timestamp=timestamp),
        )

    _feed(controller, clock, circuits, seconds=PURGE_SECONDS + DWELL_SECONDS)

    assert controller.values().charge.value is None


def test_full_status_survives_standby_loss_and_a_small_discharge():
    """Only measured heat moves the status; the modelled standby loss must not."""
    clock = Clock()
    controller = PcmChargeController(clock)

    _charge(clock, controller, PURGE_SECONDS + DWELL_SECONDS)
    assert controller.values().charge_status.value == PcmChargeStatus.FULL.value

    _feed(controller, clock, _single(inlet=20.0, outlet=20.0, flow=0.0), seconds=3600)
    assert controller.values().charge_status.value == PcmChargeStatus.FULL.value

    # A real but small discharge, kept under the deadband once purged. The dT is
    # picked well above the exhausted-effectiveness threshold so it never anchors
    # empty, whatever the duration.
    small_discharge_heat = FLOW * 3.0 * GLYCOL_20_HEAT_TRANSFER_CONVERSION
    _feed(
        controller,
        clock,
        _single(inlet=45.0, outlet=48.0, flow=FLOW),
        seconds=PURGE_SECONDS + 0.5 * PCM_STATUS_DEADBAND / small_discharge_heat,
    )
    assert controller.values().charge_status.value == PcmChargeStatus.FULL.value


def test_full_status_becomes_intermediate_after_discharging_past_the_deadband():
    clock = Clock()
    controller = PcmChargeController(clock)

    _charge(clock, controller, PURGE_SECONDS + DWELL_SECONDS)
    assert controller.values().charge_status.value == PcmChargeStatus.FULL.value

    discharge_heat = FLOW * 10.0 * GLYCOL_20_HEAT_TRANSFER_CONVERSION
    _feed(
        controller,
        clock,
        _single(inlet=45.0, outlet=55.0, flow=FLOW),
        seconds=PURGE_SECONDS + 1.5 * PCM_STATUS_DEADBAND / discharge_heat,
    )
    assert controller.values().charge_status.value == PcmChargeStatus.INTERMEDIATE.value


def test_empty_status_becomes_intermediate_after_charging_past_the_deadband():
    """Module 1's heating element can charge a module with nothing flowing."""
    clock = Clock()
    controller = PcmChargeController(clock, heating_power=PCM_HEATING_ELEMENT_POWER)

    _discharge(clock, controller, PURGE_SECONDS + DWELL_SECONDS)
    assert controller.values().charge_status.value == PcmChargeStatus.EMPTY.value

    _feed(
        controller,
        clock,
        _single(inlet=20.0, outlet=20.0, flow=0.0),
        seconds=1.5 * PCM_STATUS_DEADBAND / PCM_HEATING_ELEMENT_POWER,
        heating=True,
    )
    assert controller.values().charge_status.value == PcmChargeStatus.INTERMEDIATE.value


def test_integrated_capacity_alone_does_not_anchor_status_full():
    """The estimate can reach capacity without measured evidence of a full anchor."""
    clock = Clock()
    controller = PcmChargeController(clock)

    _discharge(clock, controller, PURGE_SECONDS + DWELL_SECONDS)
    assert controller.values().charge_status.value == PcmChargeStatus.EMPTY.value

    # Strong charging that never reads as exhausted, so it never re-anchors full.
    _feed(controller, clock, _single(inlet=70.0, outlet=60.0), seconds=20000)

    values = controller.values()
    assert values.charge.value == approx(1.0)
    assert values.charge_status.value == PcmChargeStatus.INTERMEDIATE.value
