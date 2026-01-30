import pytest
from tests.modules.conftest import compare_modelica_names, compare_yard_tags
from thrs.input_output.modules.boilers import (
    BoilersControlValues,
    BoilersSensorValues,
    BoilersSimulationInputs,
    BoilersSimulationOutputs,
)


@pytest.mark.skip("Boiler IO not complete yet")
def test_boilers_sheet_names():
    missing_in_py, missing_in_sheet = compare_modelica_names(
        ["Boilers"],
        BoilersSensorValues.zero(),
        BoilersControlValues.zero(),
        BoilersSimulationInputs.zero(),
        BoilersSimulationOutputs.zero(),
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_sheet, f"Missing in sheet: {missing_in_sheet}"


def test_yard_tags():
    compare_yard_tags(BoilersSensorValues, BoilersControlValues)
