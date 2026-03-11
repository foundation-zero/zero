from thrs.input_output.modules.lt1 import (
    Lt1ControlValues,
    Lt1SensorValues,
    Lt1SimulationInputs,
    Lt1SimulationOutputs,
)
from tests.modules.conftest import (
    compare_fmu_to_classes,
    compare_modelica_names,
    compare_yard_tags,
)
from thrs.simulation.models.fmu_paths import lt1_path


def test_lt1_sheet_names():
    missing_in_py, missing_in_sheet = compare_modelica_names(
        "LT1",
        Lt1SensorValues.zero(),
        Lt1ControlValues.zero(),
        Lt1SimulationInputs.zero(),
        Lt1SimulationOutputs.zero(),
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_sheet, f"Missing in sheet: {missing_in_sheet}"


def test_lt1_fmu_names():
    missing_in_py, missing_in_fmu = compare_fmu_to_classes(
        lt1_path,
        [
            Lt1SensorValues.zero(),
            Lt1ControlValues.zero(),
            Lt1SimulationInputs.zero(),
            Lt1SimulationOutputs.zero(),
        ],
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_fmu, f"Missing in FMU: {missing_in_fmu}"


def test_yard_tags():
    compare_yard_tags(Lt1SensorValues, Lt1ControlValues)
