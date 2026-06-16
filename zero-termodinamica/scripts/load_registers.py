# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "fastexcel",
#     "polars",
# ]
# ///
import json
from pathlib import Path

import polars as pl

SCRIPTS_FOLDER = Path(__file__).parent
EXCEL_PATH = SCRIPTS_FOLDER/ "../docs/Vent en AC lijst Termodynamica.xls"

def load_registers(path: Path, sheet_name: str = "AC"):
    df = pl.read_excel(path, sheet_name=sheet_name)
    if sheet_name == "Vent":
        df.columns = ["register_name", "address", "mode", "description", "notes"]
        df = df.tail(-3)

        df = df.with_columns( pl.col("address").cast(pl.Int32, strict=False).alias("address"))

    df = df.select(pl.all().name.to_lowercase()) \
    .select(pl.all().name.replace(" ", "_")) \
    .filter(pl.col("register_name").str.starts_with("REG_")) \
    .filter(~pl.col("register_name").str.contains("_FREE")) \
    .select(["register_name","address", "description"]) \
    .with_columns(
        pl.col("register_name").str.extract("REG_SPLIT_(\d+)").alias("reg_split"),
        pl.col("register_name").str.extract("REG_SPLIT_\d+_READ_(.*)", 1).str.replace(" ", "").alias("variable_name"),
        pl.lit(sheet_name.lower()).alias("type")
    )
    print(df)
    result = {}
    for name, data in df.group_by("reg_split"):

        # Some variables dont belong to a split, and need a different regex to get their columns
        if name[0] is None:
            data = data.with_columns(
                pl.col("register_name").str.extract("REG_SPLIT_(.*)").alias("variable_name"),
                pl.lit("ac_misc").alias("type")
            )

        reg_split = str(name[0])
        result[reg_split] = data.to_dicts()

    sorted_result = dict(sorted(result.items()))

    with open(SCRIPTS_FOLDER/f"variables_{sheet_name.lower()}.json", "w") as f:
        json.dump(sorted_result, f, indent=4)

if __name__ == "__main__":
    load_registers(EXCEL_PATH, sheet_name="Vent")
    load_registers(EXCEL_PATH, sheet_name="AC")
