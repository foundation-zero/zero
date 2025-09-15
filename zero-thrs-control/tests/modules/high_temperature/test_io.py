
from input_output.modules.high_temperature import HighTemperatureControlValues, HighTemperatureSensorValues, HighTemperatureSimulationInputs, HighTemperatureSimulationOutputs
from tests.modules.conftest import compare_fmu_to_class
from simulation.models.fmu_paths import high_temperature_path

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
