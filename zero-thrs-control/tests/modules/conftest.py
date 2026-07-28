import fmpy
import polars as pl

from thrs.input_output.base import ThrsValues
from thrs.input_output.fmu_mapping import build_fmu_key_mapping

SHEET_URL = "https://docs.google.com/spreadsheets/d/1YyfkKmqL8MZuJfStljTjhgFxawcco2cp2qCmBGFrR04/export?gid=990884182&format=csv"


def modelica_names_from_classes(classes: list[type[ThrsValues]]) -> set[str]:
    return {k for cls in classes for k in build_fmu_key_mapping(cls).values()}


def compare_modelica_names(
    module_name: str | list[str],
    sensor_values: type[ThrsValues],
    control_values: type[ThrsValues],
    simulation_inputs: type[ThrsValues],
    simulation_outputs: type[ThrsValues],
):
    """
    Compare the Modelica names in the Python code with the Modelica names in the Google Sheet.
    """
    sheet = pl.read_csv(
        SHEET_URL, skip_lines=1, schema_overrides={"Pos": pl.String, "Sub": pl.String}
    )

    if isinstance(module_name, str):
        module_name = [module_name]

    variables = set(
        sheet.lazy()
        .filter(
            pl.col("Module").is_in(module_name),
            pl.col("Included in simulation").is_in(["yes", "optional"]),
            pl.col("Variable type").is_in(
                ["Input", "Output", "Simulation input", "Simulation output"]
            ),
        )
        .collect()["Modelica name"]
        .to_list()
    )

    py_keys = modelica_names_from_classes(
        [control_values, sensor_values, simulation_inputs, simulation_outputs]
    )

    missing_in_py = variables - py_keys
    missing_in_sheet = py_keys - variables

    return missing_in_py, missing_in_sheet


def compare_fmu_to_classes(filename, classes: list[type[ThrsValues]]):
    model_description = fmpy.read_model_description(filename)

    fmu_keys = set(
        [
            var.name
            for var in model_description.modelVariables
            if var.causality == "input" or var.causality == "output"
        ]
    )
    py_keys = modelica_names_from_classes(classes)

    missing_in_py = fmu_keys - py_keys
    missing_in_fmu = py_keys - fmu_keys

    return missing_in_py, missing_in_fmu


def compare_yard_tags(
    sensor_values_cls: type[ThrsValues],
    control_values_cls: type[ThrsValues],
    exclude: set[str] | None = None,
):
    exclude = exclude or set()
    sheet = pl.read_csv(
        SHEET_URL, skip_lines=1, schema_overrides={"Pos": pl.String, "Sub": pl.String}
    )

    sheet_tags_df = (
        sheet.filter(
            pl.col("Included in simulation").is_in(["yes", "optional"]),
        )
        .with_columns(
            pl.when(pl.col("Sub") != "")
            .then(pl.concat_str(pl.col("Pos"), pl.col("Sub"), separator="-"))
            .otherwise(pl.col("Pos"))
            .alias("Tag"),
            pl.col("Technical name").str.replace_all("-", "_").alias("Technical name"),
        )
        .select(["Technical name", "Tag"])
    )

    duplicated_tags = (
        sheet_tags_df.group_by("Technical name")
        .agg(pl.col("Tag").unique())
        .filter(pl.col("Tag").list.len() > 1)
    )
    assert len(duplicated_tags) == 0, (
        f"Duplicated tags found in sheet: {duplicated_tags}"
    )
    sheet_tags = sheet_tags_df.rows_by_key("Technical name", named=True, unique=True)

    for model in [sensor_values_cls, control_values_cls]:
        for field_name, field in model.model_fields.items():
            if field_name not in exclude and isinstance(field.json_schema_extra, dict):
                yard_tag = field.json_schema_extra.get("yard_tag")
                assert sheet_tags[field_name]["Tag"] == yard_tag, (
                    f"Incorrect yard tag for {field_name}. Got {yard_tag}, expected {sheet_tags[field_name]['Tag']}"
                )
