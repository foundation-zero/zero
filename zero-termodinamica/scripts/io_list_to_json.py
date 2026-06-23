# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "fastexcel",
#     "polars",
#     "pydantic",
#     "zero-termodinamica",
# ]
#
# [tool.uv.sources]
# zero-termodinamica = { path = "../" }
# ///
from pathlib import Path
from typing import List

import polars as pl
from pydantic import TypeAdapter

from zero_termodinamica.addresses import Address, ModbusUnit, MQTTTopic

SCRIPTS_FOLDER = Path(__file__).parent
EXCEL_PATH = SCRIPTS_FOLDER / "../docs/Vent en AC lijst Termodynamica.xls"


def select_reg_split(df: pl.DataFrame, topic_prefix: str) -> List[MQTTTopic]:
    """Reg split is a repeating"""
    print(f"Select reg split: topic {topic_prefix} received {df.shape[0]} rows")
    df = df.filter(pl.col("register_name").str.contains(r"REG_SPLIT_\d\d")).filter(
        ~pl.col("register_name").str.contains("_FREE")
    )
    print(f"Select reg split: topic {topic_prefix} filtered {df.shape[0]} rows")
    df = (
        df.select(["register_name", "address", "description"])
        .with_columns(
            pl.col("register_name").str.extract(r"REG_SPLIT_(\d+)").alias("reg_split"),
            pl.col("register_name")
            .str.extract(r"REG_SPLIT_\d+_(.*)", 1)
            .str.replace("READ_", "")
            .str.replace(" ", "")
            .alias("field_name"),
        )
        .sort("reg_split", "address")
    )

    result: List[MQTTTopic] = []
    for name, data in df.group_by("reg_split"):
        reg_split = str(name[0])
        result.append(
            MQTTTopic(
                topic=f"{topic_prefix}/{reg_split}",
                fields=[
                    Address(
                        register=d["address"],
                        field_name=d["field_name"],
                        description=d["description"],
                    )
                    for d in data.select(
                        ["address", "field_name", "description"]
                    ).to_dicts()
                ],
            )
        )

    # sorted_result = dict(sorted(result, key=lambda x: int(x[0])))

    return result


def load_ac_modbus_unit(excel_path: Path, unit_id: int) -> ModbusUnit:
    df = (
        pl.read_excel(excel_path, sheet_name="AC")
        .select(pl.all().name.to_lowercase())
        .select(pl.all().name.replace(" ", "_"))
    )

    topics = select_reg_split(df, topic_prefix="termodinamica/ac")
    topics.append(
        load_flat_topic(
            df,
            topic="termodinamica/ac-misc",
            register_name_filter=[
                "REG_ABSORPTION_",
                "REG_SPLIT_ENGINE",
                "REG_SPLIT_CURRENT",
            ],
            field_name_strip=["REG_ABSORPTION_", "REG_SPLIT_"],
        )
    )

    return ModbusUnit(unit_id=unit_id, topics=topics)


def load_flat_topic(
    df: pl.DataFrame,
    topic: str,
    register_name_filter: List[str],
    field_name_strip: List[str],
) -> MQTTTopic:
    df = df.filter(
        pl.col("register_name").str.contains_any(register_name_filter)
    ).with_columns(
        pl.col("register_name")
        .str.replace("|".join(field_name_strip), "")
        .alias("field_name"),
    )
    print(f"load flat topic {topic} with {len(df)} registers")
    result: List[Address] = []
    for row in df.iter_rows(named=True):
        result.append(
            Address(
                register=row["address"],
                field_name=row["field_name"],
                description=row["description"],
            )
        )

    return MQTTTopic(topic=topic, fields=result)


if __name__ == "__main__":
    # load_registers(EXCEL_PATH, sheet_name="Vent", unit_id=33)  # Need to check slave id
    # load_registers(EXCEL_PATH, sheet_name="AC", unit_id=32)
    modbus_units = [
        load_ac_modbus_unit(excel_path=EXCEL_PATH, unit_id=32),
    ]

    result_filename = SCRIPTS_FOLDER / "../modbus_units.json"
    with open(result_filename, "w", encoding="utf-8") as f:
        json_bytes = TypeAdapter(list[ModbusUnit]).dump_json(modbus_units, indent=2)
        f.write(json_bytes.decode("utf-8"))
