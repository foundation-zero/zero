from input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
from tests.modules.conftest import compare_fmu_to_class, compare_modelica_names


def test_thrusters_sheet_names():
    missing_in_py, missing_in_sheet = compare_modelica_names(
        "Thrusters",
        ThrustersSensorValues.zero(),
        ThrustersControlValues.zero(),
        ThrustersSimulationInputs.zero(),
        ThrustersSimulationOutputs.zero(),
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_sheet, f"Missing in sheet: {missing_in_sheet}"


def test_thrusters_fmu_names(fmu_path):
    missing_in_py, missing_in_fmu = compare_fmu_to_class(
        fmu_path,
        ThrustersSensorValues.zero(),
        ThrustersControlValues.zero(),
        ThrustersSimulationInputs.zero(),
        ThrustersSimulationOutputs.zero(),
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_fmu, f"Missing in FMU: {missing_in_fmu}"
