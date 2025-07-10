from pytest import approx
from input_output.definitions.control import Valve
from input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
from tests.modules.conftest import compare_fmu_to_class, compare_modelica_names
from simulation.models.fmu_paths import thrusters_path


def test_thrusters_sheet_names():
    missing_in_py, missing_in_sheet = compare_modelica_names(
        "Thrusters",
        ThrustersSensorValues.zero(),
        ThrustersControlValues.zero(),
        ThrustersSimulationInputs.zero(),
        ThrustersSimulationOutputs.zero(),
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_sheet, f"Missing in sheet: {missing_in_sheet}"


def test_thrusters_fmu_names():
    missing_in_py, missing_in_fmu = compare_fmu_to_class(
        thrusters_path,
        ThrustersSensorValues.zero(),
        ThrustersControlValues.zero(),
        ThrustersSimulationInputs.zero(),
        ThrustersSimulationOutputs.zero(),
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_fmu, f"Missing in FMU: {missing_in_fmu}"


async def test_set_module_temperature(control, executor):
    control_values = control.initial(executor.time()).values

    executor._simulation_inputs.thrusters_aft.heat_flow.value = 0
    executor._simulation_inputs.thrusters_fwd.heat_flow.value = 0
    executor._simulation_inputs.thrusters_module_supply.temperature.value = 60

    control_values.thrusters_pump_1.dutypoint.value = 1
    control_values.thrusters_mix_aft.setpoint.value = Valve.MIXING_A_TO_AB
    control_values.thrusters_mix_fwd.setpoint.value = Valve.MIXING_A_TO_AB
    control_values.thrusters_flowcontrol_aft.setpoint.value = Valve.OPEN
    control_values.thrusters_flowcontrol_fwd.setpoint.value = Valve.OPEN
    control_values.thrusters_pump_1.on.value = True

    # allow temp to stabilize
    result = None
    for i in range(500):
        result = await executor.tick(
            control_values,
        )
    assert result is not None
    assert (
        result.sensor_values.thrusters_temperature_supply.temperature.value
        == approx(60, abs=0.1)
    )
    assert (
        result.sensor_values.thrusters_temperature_aft_mix.temperature.value
        == approx(60, abs=0.1)
    )
    assert (
        result.sensor_values.thrusters_temperature_fwd_mix.temperature.value
        == approx(60, abs=0.1)
    )


def test_schema():
    ThrustersSensorValues.model_json_schema()
    ThrustersControlValues.model_json_schema()
    ThrustersSimulationInputs.model_json_schema()
    ThrustersSimulationOutputs.model_json_schema()
