import pytest
from thrs.input_output.modules.high_temperature import (
    HighTemperatureControlValues,
    HighTemperatureSensorValues,
    HighTemperatureSimulationInputs,
    HighTemperatureSimulationOutputs,
)
from tests.modules.conftest import compare_fmu_to_class, compare_yard_tags
from thrs.simulation.models.fmu_paths import high_temperature_path


@pytest.mark.skip(reason="Need XRG to remove superfluous output variables from FMU")
def test_high_temperature_fmu_names():
    missing_in_py, missing_in_fmu = compare_fmu_to_class(
        high_temperature_path,
        HighTemperatureSensorValues.zero(),
        HighTemperatureControlValues.zero(),
        HighTemperatureSimulationInputs.zero(),
        HighTemperatureSimulationOutputs.zero(),
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_fmu, f"Missing in FMU: {missing_in_fmu}"


def test_yard_tags():
    compare_yard_tags(
        HighTemperatureSensorValues,
        HighTemperatureControlValues,
        exclude={"thrusters_pcs"},
    )
