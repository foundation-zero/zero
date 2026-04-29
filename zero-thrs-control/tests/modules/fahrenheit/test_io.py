import pytest

from tests.modules.conftest import (
    compare_fmu_to_classes,
    compare_modelica_names,
    compare_yard_tags,
)
from thrs.input_output.modules.fahrenheit import (
    FahrenheitControlValues,
    FahrenheitSensorValues,
    FahrenheitSimulationInputs,
    FahrenheitSimulationOutputs,
)
from thrs.simulation.models.fmu_paths import fahrenheit_path


@pytest.mark.io
def test_fahrenheit_sheet_names():
    missing_in_py, missing_in_sheet = compare_modelica_names(
        ["Fahrenheit"],
        FahrenheitSensorValues.zero(),
        FahrenheitControlValues.zero(),
        FahrenheitSimulationInputs.zero(),
        FahrenheitSimulationOutputs.zero(),
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_sheet, f"Missing in sheet: {missing_in_sheet}"


def test_fahrenheit_fmu_names():
    missing_in_py, missing_in_fmu = compare_fmu_to_classes(
        fahrenheit_path,
        [
            FahrenheitSensorValues.zero(),
            FahrenheitControlValues.zero(),
            FahrenheitSimulationInputs.zero(),
            FahrenheitSimulationOutputs.zero(),
        ],
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_fmu, f"Missing in FMU: {missing_in_fmu}"


@pytest.mark.io
def test_yard_tags():
    compare_yard_tags(
        FahrenheitSensorValues,
        FahrenheitControlValues,
        exclude={
            "fahrenheit_available_hot_temperature",
            "fahrenheit_available_cold_temperature",
            "fahrenheit_available_seawater_temperature",
        },
    )
