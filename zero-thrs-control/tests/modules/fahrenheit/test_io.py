from tests.modules.conftest import compare_modelica_names, compare_yard_tags
from thrs.input_output.modules.fahrenheit import (
    FahrenheitControlValues,
    FahrenheitSensorValues,
    FahrenheitSimulationInputs,
    FahrenheitSimulationOutputs,
)


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


def test_yard_tags():
    compare_yard_tags(FahrenheitSensorValues, FahrenheitControlValues)
