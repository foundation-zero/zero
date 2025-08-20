
from input_output.modules.pcm import PcmControlValues, PcmSensorValues, PcmSimulationInputs, PcmSimulationOutputs
from tests.modules.conftest import compare_fmu_to_class, compare_modelica_names
from simulation.models.fmu_paths import pcm_path


def test_pcm_sheet_names():
    missing_in_py, missing_in_sheet = compare_modelica_names(
        ["PCM"],
        PcmSensorValues.zero(),
        PcmControlValues.zero(),
        PcmSimulationInputs.zero(),
        PcmSimulationOutputs.zero(),
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_sheet, f"Missing in sheet: {missing_in_sheet}"


def test_pcm_fmu_names():
    missing_in_py, missing_in_fmu = compare_fmu_to_class(
        pcm_path,
        PcmSensorValues.zero(),
        PcmControlValues.zero(),
        PcmSimulationInputs.zero(),
        PcmSimulationOutputs.zero(),
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_fmu, f"Missing in FMU: {missing_in_fmu}"
