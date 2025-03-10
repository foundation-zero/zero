from datetime import datetime, timedelta
from pathlib import Path

from pydantic import BaseModel
from pytest import fixture

from control.modules.thrusters import simple_cooling, simple_recovery
from input_output.base import Stamped
from input_output.control import Pump, Valve
from input_output.modules.thrusters import ThrustersControls, ThrustersSensors
from simulation.executor import Executor
from simulation.fmu import Fmu
from simulation.models.thrusters.thrustersmodule import ThrustersEnvironmentals


class Parameters(BaseModel):
    pass


simple_environmentals = ThrustersEnvironmentals(
    aft_heat_flow=9000.0,
    fwd_heat_flow=4300.0,
    seawater_temperature=10.0,
    seawater_flow=50.0,
    module_inflow_temperature=50.0,
)


@fixture
def simple_thrusters():
    return Executor(
        Fmu[ThrustersControls, ThrustersSensors](
            str(
                Path(__file__).resolve().parent.parent
                / "../simulation/models/thrusters/thruster_moduleV2.fmu"
            ),
            Parameters(),
            ThrustersSensors,
            timedelta(seconds=1),
        ),
        simple_environmentals,
        datetime.now(),
        datetime.now() + timedelta(minutes=1),
        timedelta(seconds=1),
    )


def test_simple_cooling(simple_thrusters):

    simple_thrusters.set_control_values(simple_cooling(simple_thrusters.time))
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
    # from model output assert thrusters_module_inflow.flow = 0
    # from model output verify thrusters_module_outflow.flow = 0
    # from model output verify thrusters_seawater.temperature > simple_environmentals.seawater_temperature


def test_simple_recovery(simple_thrusters):

    simple_thrusters.set_control_values(simple_recovery(simple_thrusters.time))
    simple_thrusters.run()
    result = simple_thrusters.last_sensor_values

    assert (
        result.thrusters_temperature_supply.temperature.value
        < result.thrusters_temperature_aft_return.temperature.value
    )
    assert (
        result.thrusters_temperature_supply.temperature.value
        < result.thrusters_temperature_fwd_return.temperature.value
    )
    # from model output assert thrusters_module_inflow.flow > 0
    # from model output verify thrusters_module_outflow.flow > 0
    # from model output verify thrusters_module_outflow.temperature > thrusters_module_inflow.temperature
