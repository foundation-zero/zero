import pytest
from pytest import approx

from tests.modules.conftest import (
    compare_fmu_to_classes,
    compare_modelica_names,
    compare_yard_tags,
)
from tests.modules.thrusters.conftest import ThrustersSimulation
from thrs.control.modules.thrusters import ThrustersControl
from thrs.input_output.definitions.control import Valve
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
from thrs.simulation.models.fmu_paths import thrusters_path


@pytest.mark.io
def test_thrusters_sheet_names():
    missing_in_py, missing_in_sheet = compare_modelica_names(
        "Thrusters",
        ThrustersSensorValues,
        ThrustersControlValues,
        ThrustersSimulationInputs,
        ThrustersSimulationOutputs,
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_sheet, f"Missing in sheet: {missing_in_sheet}"


def test_thrusters_fmu_names():
    missing_in_py, missing_in_fmu = compare_fmu_to_classes(
        thrusters_path,
        [
            ThrustersSensorValues,
            ThrustersControlValues,
            ThrustersSimulationInputs,
            ThrustersSimulationOutputs,
        ],
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_fmu, f"Missing in FMU: {missing_in_fmu}"


@pytest.mark.io
def test_yard_tags():
    compare_yard_tags(
        ThrustersSensorValues,
        ThrustersControlValues,
        {"thrusters_mode", "thrusters_pcs"},
    )


def test_set_module_temperature(
    control: ThrustersControl,
    simulation: ThrustersSimulation,
    simulation_inputs: ThrustersSimulationInputs,
):
    control_values, _ = control.initial()

    simulation_inputs.thrusters_thruster_aft.heat_flow.value = 0  # type: ignore
    simulation_inputs.thrusters_thruster_fwd.heat_flow.value = 0  # type: ignore
    simulation_inputs.thrusters_pcm_supply.temperature.value = 60  # type: ignore

    control_values.thrusters_pump1.dutypoint.value = 1
    control_values.thrusters_mix_recovery.setpoint.value = Valve.MIXING_A_TO_AB
    control_values.thrusters_flowcontrol_aft.setpoint.value = Valve.OPEN
    control_values.thrusters_flowcontrol_fwd.setpoint.value = Valve.OPEN
    control_values.thrusters_pump1.on.value = True

    # allow temp to stabilize
    result = None
    for _i in range(500):
        result = simulation.tick(
            control_values,
        )
    assert result is not None
    assert (
        result.sensor_values.thrusters_temperature_supply.temperature.value
        == approx(60, abs=0.1)
    )
    assert (
        result.sensor_values.thrusters_temperature_recovery_mix.temperature.value
        == approx(60, abs=0.1)
    )


def test_schema():
    ThrustersSensorValues.model_json_schema()
    ThrustersControlValues.model_json_schema()
    ThrustersSimulationInputs.model_json_schema()
    ThrustersSimulationOutputs.model_json_schema()
