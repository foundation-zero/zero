from datetime import timedelta
from pathlib import Path

from pydantic import BaseModel

from input_output.base import ThrsModel
from simulation.fmu import Fmu
from simulation.input_output import SimulationInputs


class Parameters(BaseModel):
    pass


class ControlValues(ThrsModel):
    r: float


class SensorValues(ThrsModel):
    T_Raum_degC: float


class SimulationOutputs(BaseModel):
    pass


def test_fmu():
    with Fmu(
        str(
            Path(__file__).resolve().parent.parent
            / "../simulation/models/XRGTestModel/FMUInterfaceTester_MECS_regular.fmu"
        ),
        Parameters(),
        SensorValues,
        SimulationOutputs,
        timedelta(seconds=1),
    ) as fmu:
        sensor_values, _ = fmu.tick(
            ControlValues(r=1), SimulationInputs(), timedelta(seconds=1)
        )
        assert sensor_values.T_Raum_degC > -271.15
        assert fmu.solver_time == 1.0

        sensor_values, _ = fmu.tick(
            ControlValues(r=1), SimulationInputs(), timedelta(seconds=2)
        )
        assert sensor_values.T_Raum_degC > -271.15
        assert fmu.solver_time == 3.0
