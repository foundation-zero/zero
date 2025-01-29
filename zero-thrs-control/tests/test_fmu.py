from datetime import timedelta
from pathlib import Path

from pydantic import BaseModel
from simulation.fmu import Fmu


class Parameters(BaseModel):
    pass


class ControlValues(BaseModel):
    r: float


class SensorValues(BaseModel):
    T_Raum_degC: float


def test_fmu():
    with Fmu(
        str(
            Path(__file__).parent
            / "../simulation/XRGTestModel/FMUInterfaceTester_MECS_regular.fmu"
        ),
        Parameters(),
        SensorValues,
        timedelta(seconds=1),
    ) as fmu:
        result = fmu.tick(ControlValues(r=1), {}, timedelta(seconds=1))
        assert result.T_Raum_degC > -271.15
        assert fmu.time == 1.0

        result = fmu.tick(ControlValues(r=1), {}, timedelta(seconds=2))
        assert result.T_Raum_degC > -271.15
        assert fmu.time == 3.0
