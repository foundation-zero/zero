from datetime import datetime

import pytest
from pytest import approx

from tests.modules.conftest import (
    compare_fmu_to_classes,
    compare_modelica_names,
    compare_yard_tags,
)
from thrs.input_output.base import Stamped
from thrs.input_output.definitions import sensor
from thrs.input_output.definitions.units import WATER_HEAT_TRANSFER_CONVERSION
from thrs.input_output.modules.boilers import (
    BoilersControlValues,
    BoilersSensorValues,
    BoilersSimulationInputs,
    BoilersSimulationOutputs,
)

from thrs.simulation.models.fmu_paths import boilers_path


@pytest.mark.io
def test_boilers_sheet_names():
    missing_in_py, missing_in_sheet = compare_modelica_names(
        ["Boilers"],
        BoilersSensorValues.zero(),
        BoilersControlValues.zero(),
        BoilersSimulationInputs.zero(),
        BoilersSimulationOutputs.zero(),
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_sheet, f"Missing in sheet: {missing_in_sheet}"


def test_boilers_fmu_names():
    missing_in_py, missing_in_fmu = compare_fmu_to_classes(
        boilers_path,
        [
            BoilersSensorValues.zero(),
            BoilersControlValues.zero(),
            BoilersSimulationInputs.zero(),
            BoilersSimulationOutputs.zero(),
        ],
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_fmu, f"Missing in FMU: {missing_in_fmu}"


@pytest.mark.io
def test_yard_tags():
    compare_yard_tags(BoilersSensorValues, BoilersControlValues)


def test_boilers_hvac_exchanger_computed_field():
    t_supply = 60.0
    t_return = 40.0
    flow = 30.0

    values = BoilersSensorValues.zero().model_copy(
        update={
            "boilers_temperature_hvac_exchanger_return": sensor.TemperatureSensor(
                temperature=Stamped.stamp(t_supply)
            ),
            "boilers_temperature_fahrenheit_return": sensor.TemperatureSensor(
                temperature=Stamped.stamp(t_return)
            ),
            "boilers_flow_lt2": sensor.FlowSensor(
                flow=Stamped.stamp(flow),
                temperature=Stamped.stamp(0.0),
            ),
        }
    )

    exchanger = values.boilers_hvac_exchanger
    assert isinstance(exchanger, sensor.HvacExchanger)
    assert exchanger.delta_T.value == approx(t_supply - t_return)
    assert exchanger.heat.value == approx(
        flow * (t_supply - t_return) * WATER_HEAT_TRANSFER_CONVERSION
    )


def test_boilers_heatpump_computed_field():
    t_supply = 55.0
    t_return = 35.0
    flow = 20.0

    values = BoilersSensorValues.zero().model_copy(
        update={
            "boilers_temperature_boosting_supply": sensor.TemperatureSensor(
                temperature=Stamped.stamp(t_supply)
            ),
            "boilers_temperature_boosting_return": sensor.TemperatureSensor(
                temperature=Stamped.stamp(t_return)
            ),
            "boilers_flow_boosting": sensor.FlowSensor(
                flow=Stamped.stamp(flow),
                temperature=Stamped.stamp(0.0),
            ),
        }
    )

    heatpump = values.boilers_heatpump
    assert isinstance(heatpump, sensor.HeatPump)
    assert heatpump.delta_T.value == approx(t_supply - t_return)
    assert heatpump.heat.value == approx(
        flow * (t_supply - t_return) * WATER_HEAT_TRANSFER_CONVERSION
    )


def test_computed_field_timestamp_uses_oldest():
    t_old = datetime(2026, 1, 1, 12, 0, 0)
    t_new = datetime(2026, 1, 1, 12, 0, 10)

    values = BoilersSensorValues.zero().model_copy(
        update={
            "boilers_temperature_hvac_exchanger_return": sensor.TemperatureSensor(
                temperature=Stamped(value=60.0, timestamp=t_new)
            ),
            "boilers_temperature_fahrenheit_return": sensor.TemperatureSensor(
                temperature=Stamped(value=40.0, timestamp=t_old)
            ),
            "boilers_flow_lt2": sensor.FlowSensor(
                flow=Stamped(value=30.0, timestamp=t_new),
                temperature=Stamped(value=0.0, timestamp=t_new),
            ),
        }
    )

    exchanger = values.boilers_hvac_exchanger
    assert exchanger.delta_T.timestamp == t_old
    assert exchanger.heat.timestamp == t_old
