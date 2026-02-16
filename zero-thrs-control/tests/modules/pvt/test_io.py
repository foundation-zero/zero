from thrs.input_output.modules.pvt import (
    PvtControlValues,
    PvtSensorValues,
    PvtSimulationInputs,
    PvtSimulationOutputs,
)
from tests.modules.conftest import (
    compare_fmu_to_classes,
    compare_modelica_names,
    compare_yard_tags,
)
from thrs.simulation.models.fmu_paths import pvt_path


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


def test_pvt_fmu_names():
    missing_in_py, missing_in_fmu = compare_fmu_to_classes(
        pvt_path,
        [
            PvtSensorValues.zero(),
            PvtControlValues.zero(),
            PvtSimulationInputs.zero(),
            PvtSimulationOutputs.zero(),
        ],
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_fmu, f"Missing in FMU: {missing_in_fmu}"


def test_yard_tags():
    compare_yard_tags(PvtSensorValues, PvtControlValues)
