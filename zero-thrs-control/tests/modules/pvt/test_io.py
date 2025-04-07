import pytest
from input_output.modules.pvt import PvtControlValues, PvtSensorValues, PvtSimulationInputs, PvtSimulationOutputs
from tests.modules.conftest import compare_fmu_to_class, compare_modelica_names

@pytest.mark.skip("Skip until next version of FMU is available ")
def test_pvt_sheet_names():
    missing_in_py, missing_in_sheet = compare_modelica_names(
        "PVT",
        PvtSensorValues.zero(),
        PvtControlValues.zero(),
        PvtSimulationInputs.zero(),
        PvtSimulationOutputs.zero(),
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_sheet, f"Missing in sheet: {missing_in_sheet}"

def test_pvt_fmu_names(fmu_path):
    missing_in_py, missing_in_fmu = compare_fmu_to_class(
        fmu_path,
        PvtSensorValues.zero(),
        PvtControlValues.zero(),
        PvtSimulationInputs.zero(),
        PvtSimulationOutputs.zero(),
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_fmu, f"Missing in FMU: {missing_in_fmu}"
