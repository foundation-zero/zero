import fmpy
from input_output.base import ThrsModel
from input_output.fmu_mapping import build_inputs_for_fmu

import polars as pl

SHEET_URL = "https://docs.google.com/spreadsheets/d/1YyfkKmqL8MZuJfStljTjhgFxawcco2cp2qCmBGFrR04/export?gid=0&format=csv"


def modelica_names_from_class(
    sensor_values: ThrsModel,
    control_values: ThrsModel,
    simulation_inputs: ThrsModel,
    simulation_outputs: ThrsModel,
) -> set[str]:
    return set(
        {
            **build_inputs_for_fmu(control_values),
            **build_inputs_for_fmu(simulation_inputs),
            **build_inputs_for_fmu(sensor_values),
            **build_inputs_for_fmu(simulation_outputs),
        }.keys()
    )


def compare_modelica_names(
    module_name: str | list[str],
    sensor_values: ThrsModel,
    control_values: ThrsModel,
    simulation_inputs: ThrsModel,
    simulation_outputs: ThrsModel,
):
    """
    Compare the Modelica names in the Python code with the Modelica names in the Google Sheet.
    """
    sheet = pl.read_csv(SHEET_URL, skip_lines=1)

    if isinstance(module_name, str):
        module_name = [module_name]

    variables = set(
        sheet.lazy()
        .filter(
            pl.col("Simulation module").is_in(module_name),
            pl.col("Included in simulation").is_in(["yes", "optional"]),
            pl.col("Variable type").is_in(["Input", "Output", "Simulation input", "Simulation output"]),
        )
        .collect()["Modelica name"]
        .to_list()
    )

    py_keys = modelica_names_from_class(
        control_values, sensor_values, simulation_inputs, simulation_outputs
    )

    missing_in_py = variables - py_keys
    missing_in_sheet = py_keys - variables

    return missing_in_py, missing_in_sheet


def compare_fmu_to_class(
    filename, sensor_values, control_values, simulation_inputs, simulation_outputs
):
    model_description = fmpy.read_model_description(filename)

    fmu_keys = set([
        var.name
        for var in model_description.modelVariables
        if var.causality == "input" or var.causality == "output"
    ])
    py_keys = modelica_names_from_class(
        sensor_values, control_values, simulation_inputs, simulation_outputs
    )

    missing_in_py = fmu_keys - py_keys
    missing_in_fmu = py_keys - fmu_keys

    return missing_in_py, missing_in_fmu
