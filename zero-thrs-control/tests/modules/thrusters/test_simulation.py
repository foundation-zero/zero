from datetime import datetime, timedelta

import pytest
from pytest import fixture

from tests.helpers.collector import PolarsCollector
from tests.helpers.simulation_inputs import simulator_input_field_setters
from tests.helpers.simulation_runner import SimulationTestRunner
from tests.helpers.simulator_model import SimulatorModel
from tests.modules.thrusters.conftest import ThrustersSimulation
from thrs.control.modules.thrusters import (
    THRUSTERS_MODULE_DESCRIPTION,
    ThrustersControl,
    ThrustersControllerState,
    ThrustersParameters,
)
from thrs.input_output.definitions.control import Valve
from thrs.input_output.fmu_mapping import build_fmu_key_mapping
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.io_mapping import ThrsModelIoMapping, flatten_model_values
from thrs.simulation.models.fmu_paths import thrusters_path


def test_runner(simulation, fmu, simulation_inputs, control, alarms):
    io_mapping = ThrsModelIoMapping(ThrustersSensorValues, ThrustersSimulationOutputs)
    collector = PolarsCollector()
    runner = SimulationTestRunner(simulation, control, alarms)
    runner.run(20, collector)
    frame = collector.result()
    inputs = io_mapping.generate_inputs(
        ThrustersControlValues.zero(), simulation_inputs
    )
    outputs = fmu.tick(
        inputs,
        timedelta(seconds=1),
    )
    mock_fmu_outputs = io_mapping.construct_outputs(
        inputs, outputs, simulation_inputs, datetime.now()
    )[2]

    assert frame is not None
    assert frame["time"][-1] - frame["time"][0] == timedelta(seconds=19)

    not_in_fmu = set(
        {
            **flatten_model_values(
                ThrustersSensorValues.zero(),
                fmu_key_mapping=build_fmu_key_mapping(
                    ThrustersSensorValues, fmu_only=False
                ),
            ),
            **flatten_model_values(
                ThrustersControllerState.zero(),
                fmu_key_mapping=build_fmu_key_mapping(
                    ThrustersControllerState, fmu_only=False
                ),
            ),
            **flatten_model_values(
                simulation_inputs,
                fmu_key_mapping=build_fmu_key_mapping(
                    ThrustersSimulationInputs, fmu_only=False
                ),
            ),
        }
    ) - set(
        {
            **flatten_model_values(
                ThrustersSensorValues.zero(),
                fmu_key_mapping=build_fmu_key_mapping(
                    ThrustersSensorValues, fmu_only=True
                ),
            ),
            **flatten_model_values(
                simulation_inputs,
                fmu_key_mapping=build_fmu_key_mapping(
                    ThrustersSimulationInputs, fmu_only=True
                ),
            ),
        }
    )

    assert (
        set(frame.columns)
        == set(mock_fmu_outputs.keys()) | {"time", "control_mode"} | not_in_fmu
    )


def test_computed_collection(simulation: ThrustersSimulation, control, alarms):
    collector = PolarsCollector()
    runner = SimulationTestRunner(simulation, control, alarms)
    runner.run(20, collector)
    frame = collector.result()
    assert frame is not None
    assert "thrusters_temperature_recovery__temperature__C" in frame.columns


def test_simulation(simulation_inputs, control, alarms):
    thrusters_model = SimulatorModel(
        fmu_path=thrusters_path,
        sensor_values_cls=ThrustersSensorValues,
        control_values_cls=ThrustersControlValues,
        control_cls=ThrustersControl,
        simulation_outputs_cls=ThrustersSimulationOutputs,
        simulation_inputs=simulation_inputs,
        alarms=alarms,
    )

    with thrusters_model.simulation() as simulation:
        runner = SimulationTestRunner.from_module(
            THRUSTERS_MODULE_DESCRIPTION, ThrustersParameters(), simulation
        )

        collector = PolarsCollector()

        runner.run(20, collector)

        result = collector.result()
        assert result is not None
        assert result["time"].len() == 20


@fixture(params=list(simulator_input_field_setters(ThrustersSimulationInputs)))
def incorrect_simulation_inputs(simulation_inputs, request):
    inputs = simulation_inputs.get_values_at_time(datetime.now())
    request.param(inputs, -9e7)
    return inputs


def test_thrusters_simulation_inputs(incorrect_simulation_inputs, control):
    with Fmu(thrusters_path) as fmu:
        simulation = Simulation(
            ThrustersSensorValues,
            ThrustersSimulationOutputs,
            fmu,
            incorrect_simulation_inputs,
            datetime.now(),
            timedelta(seconds=5),
        )

        control_values, _ = control.initial()

        control_values.thrusters_pump1.dutypoint.value = 1
        control_values.thrusters_mix_recovery.setpoint.value = Valve.MIXING_A_TO_AB
        control_values.thrusters_flowcontrol_aft.setpoint.value = Valve.OPEN
        control_values.thrusters_flowcontrol_fwd.setpoint.value = Valve.OPEN
        control_values.thrusters_pump1.on.value = True

        with pytest.raises(Exception):
            for i in range(100):
                simulation.tick(
                    control._current_values,
                )
