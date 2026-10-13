import pytest

from tests.modules.conftest import compare_modelica_names, compare_yard_tags
from thrs.input_output.modules.cooling import (
    CoolingPanelsControlValues,
    CoolingPanelsSensorValues,
    CoolingPanelsSimulationInputs,
    CoolingPanelsSimulationOutputs,
)


@pytest.mark.io
def test_cooling_panels_sheet_names():
    missing_in_py, missing_in_sheet = compare_modelica_names(
        ["Cooling"],
        CoolingPanelsSensorValues,
        CoolingPanelsControlValues,
        CoolingPanelsSimulationInputs,
        CoolingPanelsSimulationOutputs,
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_sheet, f"Missing in sheet: {missing_in_sheet}"


@pytest.mark.io
def test_yard_tags():
    compare_yard_tags(
        CoolingPanelsSensorValues,
        CoolingPanelsControlValues,
        exclude={"cooling_mode"},
    )
