import polars as pl

from input_output.base import ThrsModel
from input_output.fmu_mapping import build_inputs_for_fmu
from input_output.modules.pvt import (
    PvtControlValues,
    PvtSensorValues,
    PvtSimulationInputs,
    PvtSimulationOutputs,
)
from input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)

# TODO: before open sourcing set to view only on link
SHEET_URL = "https://docs.google.com/spreadsheets/d/1YyfkKmqL8MZuJfStljTjhgFxawcco2cp2qCmBGFrR04/export?gid=0&format=csv"


def compare_modelica_names(
    module_name: str,
    sensor_values: ThrsModel,
    control_values: ThrsModel,
    simulation_inputs: ThrsModel,
    simulation_outputs: ThrsModel,
):
    """
    Compare the Modelica names in the Python code with the Modelica names in the Google Sheet.
    """
    sheet = pl.read_csv(SHEET_URL, skip_lines=1)

    variables = set(
        sheet.lazy()
        .filter(
            pl.col("Simulation module") == module_name,
            pl.col("Included in simulation").is_in(["yes", "optional"]),
        )
        .collect()["Modelica name"]
        .to_list()
    )

    py_keys = set(
        {
            **build_inputs_for_fmu(control_values),
            **build_inputs_for_fmu(simulation_inputs),
            **build_inputs_for_fmu(sensor_values),
            **build_inputs_for_fmu(simulation_outputs),
        }.keys()
    )
    missing_in_py = variables - py_keys
    missing_in_sheet = py_keys - variables

    return missing_in_py, missing_in_sheet


def test_thrusters_names():
    missing_in_py, missing_in_sheet = compare_modelica_names(
        "Thrusters",
        ThrustersSensorValues.zero(),
        ThrustersControlValues.zero(),
        ThrustersSimulationInputs.zero(),
        ThrustersSimulationOutputs.zero(),
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_sheet, f"Missing in sheet: {missing_in_sheet}"


def test_pvt_names():
    missing_in_py, missing_in_sheet = compare_modelica_names(
        "PVT",
        PvtSensorValues.zero(),
        PvtControlValues.zero(),
        PvtSimulationInputs.zero(),
        PvtSimulationOutputs.zero(),
    )

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_sheet, f"Missing in sheet: {missing_in_sheet}"
