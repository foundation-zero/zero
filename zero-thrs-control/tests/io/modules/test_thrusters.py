import polars as pl

from input_output.modules.thrusters import ThrustersSensors

# TODO: before open sourcing set to view only on link
SHEET_URL = "https://docs.google.com/spreadsheets/d/1YyfkKmqL8MZuJfStljTjhgFxawcco2cp2qCmBGFrR04/export?gid=0&format=csv"


def test_modelica_names():
    zero = ThrustersSensors.zero()
    sheet = pl.read_csv(SHEET_URL, skip_lines=1)
    thruster_sensors = set(
        sheet.lazy()
        .filter(
            (pl.col("Simulation module") == "Thrusters")
            & (pl.col("Variable type") == "Output")
            & (pl.col("Included in simulation") == "yes")
        )
        .collect()["Modelica name"]
        .to_list()
    )
    py_keys = set(zero.values_for_fmu().keys())

    missing_in_py = thruster_sensors - py_keys
    missing_in_sheet = py_keys - thruster_sensors

    assert not missing_in_py, f"Missing in Python: {missing_in_py}"
    assert not missing_in_sheet, f"Missing in sheet: {missing_in_sheet}"
