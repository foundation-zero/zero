from datetime import timedelta
from pathlib import Path

import polars as pl
from pytest import fixture

from input_output.fmu_mapping import build_inputs_for_fmu
from input_output.modules.thrusters import (ThrustersControlValues,
                                            ThrustersSensorValues,
                                            ThrustersSimulationInputs,
                                            ThrustersSimulationOutputs)
from simulation.executor import Executor
from simulation.fmu import Fmu

# TODO: before open sourcing set to view only on link
SHEET_URL = "https://docs.google.com/spreadsheets/d/1YyfkKmqL8MZuJfStljTjhgFxawcco2cp2qCmBGFrR04/export?gid=0&format=csv"


@fixture
def executor():
    return Executor(
        Fmu(
            str(
                Path(__file__).resolve().parent.parent
                / "../../simulation/models/thrusters/thruster_moduleV4.fmu"
            ),
            timedelta(seconds=0.1),
        ),
        ThrustersSensorValues,
        ThrustersSimulationOutputs,
    )


def test_modelica_names(executor):
    sheet = pl.read_csv(SHEET_URL, skip_lines=1)
    thrusters_variables = set(
        sheet.lazy()
        .filter(
            (pl.col("Simulation module") == "Thrusters")
            & (pl.col("Included in simulation") == "yes")
        )
        .collect()["Modelica name"]
        .to_list()
    )

    py_inputs_keys = set(
        {
            **build_inputs_for_fmu(ThrustersControlValues.zero()),
            **build_inputs_for_fmu(ThrustersSimulationInputs.zero()),
        }.keys()
    )
    py_outputs_keys = set(
        build_inputs_for_fmu(
            ThrustersSensorValues.zero(), ThrustersSimulationOutputs.zero()  # type: ignore
        ).keys()
    )

    missing_in_py = thrusters_variables - py_inputs_keys - py_outputs_keys
    missing_in_sheet = py_inputs_keys.union(py_outputs_keys) - thrusters_variables

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_sheet, f"Missing in sheet: {missing_in_sheet}"
