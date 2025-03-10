from datetime import datetime, timedelta
from pathlib import Path

from pydantic import BaseModel

from input_output.base import ThrsModel
from simulation.environmentals import Environmentals
from simulation.executor import Executor
from simulation.fmu import Fmu


class Parameters(BaseModel):
    pass


class ControlValues(ThrsModel):
    r: float


class SensorValues(ThrsModel):
    T_Raum_degC: float


def test_executor():

    start_time = datetime.now()
    executor = Executor(
        Fmu(
            str(
                Path(__file__).resolve().parent.parent
                / "../simulation/models/XRGTestModel/FMUInterfaceTester_MECS_regular.fmu"
            ),
            Parameters(),
            SensorValues,
            timedelta(seconds=0.1),
        ),
        Environmentals(),
        start_time,
        start_time + timedelta(seconds=2),
        timedelta(seconds=1),
    )

    executor.set_control_values(ControlValues(r=1))
    executor.run()
    assert executor._time == start_time + timedelta(seconds=2)
    assert executor._last_sensor_values.T_Raum_degC > -271.15
