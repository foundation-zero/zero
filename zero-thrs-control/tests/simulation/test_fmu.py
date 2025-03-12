from datetime import timedelta
from pathlib import Path

from pydantic import BaseModel
from pytest import approx

from input_output.base import ThrsModel
from simulation.fmu import Fmu
from simulation.input_output import SimulationInputs


def test_fmu():
    with Fmu(
        str(
            Path(__file__).resolve().parent.parent
            / "../simulation/models/XRGTestModel/FMUInterfaceTester_MECS_regular.fmu"
        ),
        timedelta(seconds=0.2),
    ) as fmu:
        outputs = fmu.tick({"r": 1.0}, timedelta(seconds=1))
        assert outputs["T_Raum_degC"] > -271.15
        assert fmu.solver_time == approx(1.0)

        outputs = fmu.tick({"r": 1.0}, timedelta(seconds=2))
        assert outputs["T_Raum_degC"] > -271.15
        assert fmu.solver_time == approx(3.0)
