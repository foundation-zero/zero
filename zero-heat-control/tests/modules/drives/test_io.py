import pytest

from tests.modules.conftest import (
    compare_fmu_to_classes,
    compare_modelica_names,
    compare_yard_tags,
)
from thrs.input_output.modules.drives import (
    DrivesControlValues,
    DrivesSensorValues,
    DrivesSimulationInputs,
    DrivesSimulationOutputs,
)
from thrs.simulation.models.fmu_paths import drives_path


@pytest.mark.io
def test_drives_sheet_names():
    missing_in_py, missing_in_sheet = compare_modelica_names(
        "Drives",
        DrivesSensorValues,
        DrivesControlValues,
        DrivesSimulationInputs,
        DrivesSimulationOutputs,
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_sheet, f"Missing in sheet: {missing_in_sheet}"


def test_drives_fmu_names():
    missing_in_py, missing_in_fmu = compare_fmu_to_classes(
        drives_path,
        [
            DrivesSensorValues,
            DrivesControlValues,
            DrivesSimulationInputs,
            DrivesSimulationOutputs,
        ],
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_fmu, f"Missing in FMU: {missing_in_fmu}"


@pytest.mark.io
def test_yard_tags():
    compare_yard_tags(
        DrivesSensorValues,
        DrivesControlValues,
        exclude={"drives_mode"},
    )
