from datetime import datetime

import pytest

from thrs.control.controllers import ChargeController
from thrs.control.modules.pcm import PcmControllerState
from thrs.input_output.base import Stamped
from thrs.input_output.definitions import sensor
from thrs.input_output.definitions.controllers import PcmChargingState
from thrs.input_output.definitions.units import WATER_HEAT_TRANSFER_CONVERSION

FLOW = 5.0


def _heat_exchanger(
    supply: float, module: float, flow: float = FLOW
) -> sensor.HeatExchanger:
    return sensor.HeatExchanger.from_sensors(
        temperature_supply=Stamped.stamp(supply),
        temperature_return=Stamped.stamp(module),
        flow=Stamped.stamp(flow),
        heat_transfer_conversion=WATER_HEAT_TRANSFER_CONVERSION,
    )


def test_charging_when_heat_below_negative_deadband():
    heat_device = _heat_exchanger(supply=70.0, module=50.0)

    controller = ChargeController(datetime.now)
    controller(heat_device)

    controller_values = controller.values()

    assert controller_values.charging_state.value == PcmChargingState.CHARGING.value


def test_discharging_when_heat_above_deadband():
    heat_device = _heat_exchanger(supply=50.0, module=70.0)

    controller = ChargeController(datetime.now)
    controller(heat_device)

    controller_values = controller.values()

    assert controller_values.charging_state.value == PcmChargingState.DISCHARGING.value


# ~0.7 W at nominal flow, well within the 100 W deadband
@pytest.mark.parametrize("module", [70.002, 69.998])
def test_idle_within_deadband(module: float):
    heat_device = _heat_exchanger(supply=70.0, module=module)

    controller = ChargeController(datetime.now)
    controller(heat_device)

    controller_values = controller.values()

    assert controller_values.charging_state.value == PcmChargingState.IDLE.value


def test_idle_at_zero_flow_despite_temperature_difference():
    heat_device = _heat_exchanger(supply=70.0, module=50.0, flow=0.0)

    controller = ChargeController(datetime.now)
    controller(heat_device)

    controller_values = controller.values()

    assert controller_values.charging_state.value == PcmChargingState.IDLE.value


def test_module_computed_field_idle_by_default():
    controller_state = PcmControllerState.zero()

    charge_controller = controller_state.module1_charge_controller

    assert charge_controller.charging_state.value == PcmChargingState.IDLE.value
    assert charge_controller.charge.value == 0
