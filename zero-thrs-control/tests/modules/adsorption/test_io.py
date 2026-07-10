import pytest

from tests.modules.conftest import (
    compare_fmu_to_classes,
    compare_modelica_names,
    compare_yard_tags,
)
from thrs.input_output.modules.adsorption import (
    AdsorptionControlValues,
    AdsorptionSensorValues,
    AdsorptionSimulationInputs,
    AdsorptionSimulationOutputs,
)
from thrs.simulation.models.fmu_paths import adsorption_path


@pytest.mark.io
def test_adsorption_sheet_names():
    missing_in_py, missing_in_sheet = compare_modelica_names(
        ["Adsorption"],
        AdsorptionSensorValues,
        AdsorptionControlValues,
        AdsorptionSimulationInputs,
        AdsorptionSimulationOutputs,
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_sheet, f"Missing in sheet: {missing_in_sheet}"


def test_adsorption_fmu_names():
    missing_in_py, missing_in_fmu = compare_fmu_to_classes(
        adsorption_path,
        [
            AdsorptionSensorValues,
            AdsorptionControlValues,
            AdsorptionSimulationInputs,
            AdsorptionSimulationOutputs,
        ],
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_fmu, f"Missing in FMU: {missing_in_fmu}"


@pytest.mark.io
def test_yard_tags():
    compare_yard_tags(
        AdsorptionSensorValues,
        AdsorptionControlValues,
        exclude={
            "adsorption_available_hot_temperature",
            "adsorption_available_cold_temperature",
            "adsorption_available_seawater_temperature",
        },
    )
