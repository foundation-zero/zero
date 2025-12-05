import re
from thrs.input_output.modules.high_temperature import (
    HighTemperatureControlValues,
    HighTemperatureSensorValues,
    HighTemperatureSimulationInputs,
    HighTemperatureSimulationOutputs,
)
from tests.modules.conftest import compare_fmu_to_class, compare_yard_tags
from thrs.simulation.models.fmu_paths import high_temperature_path


def test_high_temperature_fmu_names():
    missing_in_py, missing_in_fmu = compare_fmu_to_class(
        high_temperature_path,
        HighTemperatureSensorValues.zero(),
        HighTemperatureControlValues.zero(),
        HighTemperatureSimulationInputs.zero(),
        HighTemperatureSimulationOutputs.zero(),
    )
    missing_in_py_excluding_superfluous_outputs = {
        item for item in missing_in_py if not re.match(r"^z_.*\.", item)
    }  # Remove superfluous outputs contained in the High Temperature FMU due to the way it's constructed (combining submodules)
    assert not missing_in_py_excluding_superfluous_outputs, (
        f"Missing in Python: {missing_in_py_excluding_superfluous_outputs}"
    )
    assert not missing_in_fmu, f"Missing in FMU: {missing_in_fmu}"


def test_yard_tags():
    compare_yard_tags(
        HighTemperatureSensorValues,
        HighTemperatureControlValues,
        exclude={"thrusters_pcs"},
    )
