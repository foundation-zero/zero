from tests.modules.conftest import compare_fmu_to_classes
from thrs.input_output.modules.consumers import (
    ConsumersControlValues,
    ConsumersSensorValues,
)
from thrs.input_output.modules.high_temperature import (
    HighTemperatureSimulationInputs,
    HighTemperatureSimulationOutputs,
)

from thrs.input_output.modules.pcm import PcmControlValues, PcmSensorValues
from thrs.input_output.modules.pvt import PvtControlValues, PvtSensorValues
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
)
from thrs.simulation.models.fmu_paths import high_temperature_path


def test_high_temperature_fmu_names():
    missing_in_py, missing_in_fmu = compare_fmu_to_classes(
        high_temperature_path,
        [
            HighTemperatureSimulationInputs.zero(),
            HighTemperatureSimulationOutputs.zero(),
            ThrustersSensorValues.zero(),
            ThrustersControlValues.zero(),
            PvtSensorValues.zero(),
            PvtControlValues.zero(),
            PcmSensorValues.zero(),
            PcmControlValues.zero(),
            ConsumersSensorValues.zero(),
            ConsumersControlValues.zero(),
        ],
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_fmu, f"Missing in FMU: {missing_in_fmu}"
