import polars as pl
import pytest

from input_output.fmu_mapping import build_inputs_for_fmu
from input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)

# TODO: before open sourcing set to view only on link
SHEET_URL = "https://docs.google.com/spreadsheets/d/1YyfkKmqL8MZuJfStljTjhgFxawcco2cp2qCmBGFrR04/export?gid=0&format=csv"


@pytest.mark.skip("Skip until V7 of FMU is available ")
def test_modelica_names():
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

    py_keys = set(
        {
            **build_inputs_for_fmu(ThrustersControlValues.zero()),
            **build_inputs_for_fmu(ThrustersSimulationInputs.zero()),
            **build_inputs_for_fmu(ThrustersSensorValues.zero()),
            **build_inputs_for_fmu(ThrustersSimulationOutputs.zero()),
        }.keys()
    )
    missing_in_py = thrusters_variables - py_keys
    missing_in_sheet = py_keys - thrusters_variables

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_sheet, f"Missing in sheet: {missing_in_sheet}"
