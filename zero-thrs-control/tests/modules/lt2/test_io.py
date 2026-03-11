from thrs.input_output.modules.lt2 import (
    Lt2ControlValues,
    Lt2SensorValues,
    Lt2SimulationInputs,
    Lt2SimulationOutputs,
)
from tests.modules.conftest import (
    compare_fmu_to_classes,
    compare_modelica_names,
    compare_yard_tags,
)
from thrs.simulation.models.fmu_paths import lt2_path


def test_lt2_sheet_names():
    missing_in_py, missing_in_sheet = compare_modelica_names(
        "LT2",
        Lt2SensorValues.zero(),
        Lt2ControlValues.zero(),
        Lt2SimulationInputs.zero(),
        Lt2SimulationOutputs.zero(),
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_sheet, f"Missing in sheet: {missing_in_sheet}"


def test_lt2_fmu_names():
    missing_in_py, missing_in_fmu = compare_fmu_to_classes(
        lt2_path,
        [
            Lt2SensorValues.zero(),
            Lt2ControlValues.zero(),
            Lt2SimulationInputs.zero(),
            Lt2SimulationOutputs.zero(),
        ],
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_fmu, f"Missing in FMU: {missing_in_fmu}"


def test_yard_tags():
    compare_yard_tags(Lt2SensorValues, Lt2ControlValues)
