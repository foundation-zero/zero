from datetime import timedelta
from pathlib import Path

from pytest import approx

from simulation.fmu import Fmu


def test_fmu():
    with Fmu(
        str(
            Path(__file__).resolve().parent.parent.parent
            / "src/simulation/models/XRGTestModel/FMUInterfaceTester_MECS_regular.fmu"
        )
    ) as fmu:
        outputs = fmu.tick({"r": 1.0}, timedelta(seconds=1))
        assert outputs["T_Raum_degC"] > -271.15
        assert fmu.solver_time == approx(2)

        outputs = fmu.tick({"r": 1.0}, timedelta(seconds=2))
        assert outputs["T_Raum_degC"] > -271.15
        assert fmu.solver_time == approx(4)
