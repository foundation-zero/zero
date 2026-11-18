from tests.modules.conftest import compare_fmu_to_classes
from tests.modules.pcm.test_io import PCM_IGNORED_FMU_CHARGED_OUTPUTS
from thrs.control.modules.consumers.io import (
    ConsumersControlValues,
    ConsumersSensorValues,
)
from thrs.control.modules.high_temperature.io import (
    HighTemperatureSimulationInputs,
    HighTemperatureSimulationOutputs,
)
from thrs.control.modules.pcm.io import PcmControlValues, PcmSensorValues
from thrs.control.modules.pvt.io import PvtControlValues, PvtSensorValues
from thrs.control.modules.thrusters.io import (
    ThrustersControlValues,
    ThrustersSensorValues,
)
from thrs.simulation.models.fmu_paths import high_temperature_path


def test_high_temperature_fmu_names():
    missing_in_py, missing_in_fmu = compare_fmu_to_classes(
        high_temperature_path,
        [
            HighTemperatureSimulationInputs,
            HighTemperatureSimulationOutputs,
            ThrustersSensorValues,
            ThrustersControlValues,
            PvtSensorValues,
            PvtControlValues,
            PcmSensorValues,
            PcmControlValues,
            ConsumersSensorValues,
            ConsumersControlValues,
        ],
    )
    missing_in_py -= PCM_IGNORED_FMU_CHARGED_OUTPUTS

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_fmu, f"Missing in FMU: {missing_in_fmu}"
