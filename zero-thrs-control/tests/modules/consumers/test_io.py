from input_output.modules.consumers import (
    ConsumersControlValues,
    ConsumersSensorValues,
    ConsumersSimulationInputs,
    ConsumersSimulationOutputs,
)
from tests.modules.conftest import compare_fmu_to_class, compare_modelica_names
from simulation.models.fmu_paths import consumers_path


def test_consumers_sheet_names():
    missing_in_py, missing_in_sheet = compare_modelica_names(
        ["Consumers"],
        ConsumersSensorValues.zero(),
        ConsumersControlValues.zero(),
        ConsumersSimulationInputs.zero(),
        ConsumersSimulationOutputs.zero(),
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_sheet, f"Missing in sheet: {missing_in_sheet}"


def test_consumers_fmu_names():
    missing_in_py, missing_in_fmu = compare_fmu_to_class(
        consumers_path,
        ConsumersSensorValues.zero(),
        ConsumersControlValues.zero(),
        ConsumersSimulationInputs.zero(),
        ConsumersSimulationOutputs.zero(),
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_fmu, f"Missing in FMU: {missing_in_fmu}"
