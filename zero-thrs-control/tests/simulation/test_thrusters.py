from datetime import datetime, timedelta
from pathlib import Path

from pydantic import BaseModel
from pytest import fixture

from control.modules.thrusters import ThrustersControl, ThrustersSetpoints
from input_output.modules.thrusters import (ThrustersControlValues,
                                            ThrustersSensors)
from simulation.executor import Executor
from simulation.fmu import Fmu
from simulation.models.thrusters.thrusters_io import ThrustersSimulationInputs


class Parameters(BaseModel):
    pass


simple_inputs = ThrustersSimulationInputs(
    aft_heat_flow=9000.0,
    fwd_heat_flow=4300.0,
    seawater_supply_temperature=10.0,
    seawater_supply_flow=50.0,
    module_supply_temperature=50.0,
)


@fixture
def simple_thrusters() -> Executor[ThrustersControlValues, ThrustersSensors]:
    return Executor(
        Fmu[ThrustersControlValues, ThrustersSensors](
            str(
                Path(__file__).resolve().parent.parent
                / "../simulation/models/thrusters/thruster_moduleV3.fmu"
            ),
            Parameters(),
            ThrustersSensors,
            timedelta(seconds=1),
        ),
        simple_inputs,
        datetime.now(),
        datetime.now() + timedelta(minutes=1),
        timedelta(seconds=1),
    )


@fixture
def thrusters_control() -> ThrustersControl:
    return ThrustersControl(ThrustersSetpoints(cooling_mix_setpoint=40.0))


def test_simple_cooling(simple_thrusters, thrusters_control):

    simple_thrusters.set_control_values(
        thrusters_control.simple_cooling(
            simple_thrusters.last_sensor_values, simple_thrusters.time
        )
    )
    simple_thrusters.run()
    sensors = simple_thrusters.last_sensor_values

    assert (
        sensors.thrusters_temperature_supply.temperature.value
        < sensors.thrusters_temperature_aft_return.temperature.value
    )
    assert (
        sensors.thrusters_temperature_supply.temperature.value
        < sensors.thrusters_temperature_fwd_return.temperature.value
    )
    # from model output assert thrusters_module_supply.flow = 0
    # from model output verify thrusters_module_return.flow = 0
    # from model output verify thrusters_seawater_supply.temperature < thrusters_seawater_return.temperature


def test_simple_recovery(simple_thrusters, thrusters_control):
    simple_thrusters.set_control_values(
        thrusters_control.simple_recovery(simple_thrusters.time)
    )
    simple_thrusters.run()
    sensors = simple_thrusters.last_sensor_values

    assert (
        sensors.thrusters_temperature_supply.temperature.value
        < sensors.thrusters_temperature_aft_return.temperature.value
    )
    assert (
        sensors.thrusters_temperature_supply.temperature.value
        < sensors.thrusters_temperature_fwd_return.temperature.value
    )
    assert (
        sensors.thrusters_temperature_aft_supply.flow.value
        == sensors.thrusters_temperature_fwd_supply.flow.value
        == sensors.thrusters_module_supply.flow.value
    )
    # from model output assert thrusters_module_supply.flow > 0
    # from model output verify thrusters_module_return.flow > 0
    # from model output verify thrusters_module_return.temperature > thrusters_module_supply.temperature
