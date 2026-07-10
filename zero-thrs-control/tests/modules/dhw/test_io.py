from datetime import datetime

import pytest
from pytest import approx

from tests.modules.conftest import (
    compare_fmu_to_classes,
    compare_modelica_names,
    compare_yard_tags,
)
from thrs.input_output.base import Stamped
from thrs.input_output.definitions import control, sensor
from thrs.input_output.definitions.units import WATER_HEAT_TRANSFER_CONVERSION
from thrs.input_output.fmu_mapping import included_in_fmu
from thrs.input_output.modules.dhw import (
    DhwControlValues,
    DhwSensorValues,
    DhwSimulationInputs,
    DhwSimulationOutputs,
)
from thrs.simulation.models.fmu_paths import dhw_path


@pytest.mark.io
def test_dhw_sheet_names():
    missing_in_py, missing_in_sheet = compare_modelica_names(
        ["DHW"],
        DhwSensorValues,
        DhwControlValues,
        DhwSimulationInputs,
        DhwSimulationOutputs,
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_sheet, f"Missing in sheet: {missing_in_sheet}"


def test_dhw_fmu_names():
    missing_in_py, missing_in_fmu = compare_fmu_to_classes(
        dhw_path,
        [
            DhwSensorValues,
            DhwControlValues,
            DhwSimulationInputs,
            DhwSimulationOutputs,
        ],
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_fmu, f"Missing in FMU: {missing_in_fmu}"


@pytest.mark.io
def test_yard_tags():
    compare_yard_tags(
        DhwSensorValues,
        DhwControlValues,
        {
            "freshwater_hotwater_flow",
            "freshwater_hotwater_temperature",
            "dhw_tanks_controller",
            "dhw_pump_flow_controller",
            "dhw_pump_temperature_controller",
            "dhw_drives_flow_controller",
            "dhw_dc_flow_controller",
        },
    )


def test_dhw_hvac_exchanger_computed_field():
    t_supply = 60.0
    t_return = 40.0
    flow = 30.0

    values = DhwSensorValues.zero().model_copy(
        update={
            "dhw_temperature_hvac_exchanger_return": sensor.TemperatureSensor(
                temperature=Stamped.stamp(t_return)
            ),
            "dhw_temperature_adsorption_return": sensor.TemperatureSensor(
                temperature=Stamped.stamp(t_supply)
            ),
            "dhw_flow_dc": sensor.FlowSensor(
                flow=Stamped.stamp(flow),
                temperature=Stamped.stamp(0.0),
            ),
        }
    )

    exchanger = values.dhw_hvac_exchanger
    assert isinstance(exchanger, sensor.HvacExchanger)
    assert exchanger.delta_t.value == approx(-20.0)
    assert exchanger.heat.value == approx(30.0 * -20.0 * WATER_HEAT_TRANSFER_CONVERSION)


def test_dhw_heatpump_computed_field():
    t_supply = 35.0
    t_return = 55.0
    flow = 20.0

    values = DhwSensorValues.zero().model_copy(
        update={
            "dhw_temperature_boosting_return": sensor.TemperatureSensor(
                temperature=Stamped.stamp(t_return)
            ),
            "dhw_temperature_boosting_supply": sensor.TemperatureSensor(
                temperature=Stamped.stamp(t_supply)
            ),
            "dhw_flow_boosting": sensor.FlowSensor(
                flow=Stamped.stamp(flow),
                temperature=Stamped.stamp(0.0),
            ),
            "dhw_switch_heatpump": sensor.Valve(
                position_rel=Stamped.stamp(control.Valve.OPEN)
            ),
            "dhw_switch_high_temperature": sensor.Valve(
                position_rel=Stamped.stamp(control.Valve.CLOSED)
            ),
        }
    )

    heatpump = values.dhw_heatpump
    assert isinstance(heatpump, sensor.HeatPump)
    assert heatpump.delta_t.value == approx(20.0)
    assert heatpump.heat.value == approx(20.0 * 20.0 * WATER_HEAT_TRANSFER_CONVERSION)


def test_computed_field_timestamp_uses_oldest():
    t_old = datetime(2026, 1, 1, 12, 0, 0)
    t_new = datetime(2026, 1, 1, 12, 0, 10)

    values = DhwSensorValues.zero().model_copy(
        update={
            "dhw_temperature_hvac_exchanger_return": sensor.TemperatureSensor(
                temperature=Stamped(value=60.0, timestamp=t_new)
            ),
            "dhw_temperature_adsorption_return": sensor.TemperatureSensor(
                temperature=Stamped(value=40.0, timestamp=t_old)
            ),
            "dhw_flow_dc": sensor.FlowSensor(
                flow=Stamped(value=30.0, timestamp=t_new),
                temperature=Stamped(value=0.0, timestamp=t_new),
            ),
        }
    )

    exchanger = values.dhw_hvac_exchanger
    assert exchanger.delta_t.timestamp == t_old
    assert exchanger.heat.timestamp == t_old


def test_all_computed_fields_evaluate():
    values = DhwSensorValues.zero()
    for name in DhwSensorValues.model_computed_fields:
        result = getattr(values, name)
        assert result is not None, f"Computed field '{name}' returned None"


def test_all_non_fmu_sensor_fields_have_simulation_source():
    non_fmu_sensor_fields = {
        name
        for name, field in DhwSensorValues.model_fields.items()
        if not included_in_fmu(field)
    }

    simulation_inputs_sources = set(DhwSimulationInputs.model_fields) | set(
        DhwSimulationInputs.model_computed_fields
    )
    simulation_outputs_sources = set(DhwSimulationOutputs.model_fields) | set(
        DhwSimulationOutputs.model_computed_fields
    )
    all_sources = simulation_inputs_sources | simulation_outputs_sources

    missing = non_fmu_sensor_fields - all_sources
    assert not missing, (
        f"Non-FMU sensor fields with no simulation input/output source: {missing}\n"
    )
