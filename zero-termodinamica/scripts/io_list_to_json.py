from pathlib import Path
from typing import List

import polars as pl
from pydantic import TypeAdapter

from zero_termodinamica.io import Address, LiteralField, ModbusUnit, MqttTopic

SCRIPTS_FOLDER = Path(__file__).parent
EXCEL_PATH = SCRIPTS_FOLDER / "../docs/Vent en AC lijst Termodynamica.xls"

REG_ROOM_MAPPING = {
    "01": "Tech room",
    "02": "Lounge",
    "03": "Guest cabin (Aft SB)",
    "04": "Bathroom (Aft SB)",
    "05": "Guest cabin (PS)",
    "06": "Master bathroom cabin (PS)",
    "07": "Master cabin (PS)",
    "08": "Master cabin (SB)",
    "09": "Guest cabin (SB)",
    "10": "Office area (Fwd)",
    "11": "Guest cabin (Fr.42 Mid PS)",
    "12": "Mission Room",
    "13": "Laundry",
    "14": "Captain cabin",
    "15": "Crew area (Fwd)",
    "16": "Crew cabin (Fwd PS)",
    "17": "Watersport storage",
    "18": "Galley",
    "19": "Crew mess",
    "20": "Crew cabin (Aft)",
    "21": "Crew cabin (Mid SB)",
    "22": "Crew cabin (SB)",
    "23": "Main deckhouse",
    "24": "Aft area",
    "25": "Aft area (Slave)",
    "26": "Office area (Fwd)",
    "27": "Guest cabin (Fr.42 Mid PS)",
    "28": "Guest cabin (FR.55 Aft PS)",
    "29": "Navcom",
    "30": "HM10 Backup Cooling Panels",
    "31": "Crew cabin (Fwd SB)",
}


def select_nested_ac_topics(df: pl.DataFrame, topic_prefix: str) -> List[MqttTopic]:
    """Ac topics on termondamica/ac/[split_id] are nested topics with the same schema."""
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
            .str.to_lowercase()
            .str.replace("pwr", "power")
            .str.replace("humi", "humidity")
            .str.replace("air_in", "air_temperature_in")
            .str.replace("sp_room", "setpoint_room_temperature")
            .alias("field_name"),
        )
        # "AIR_IN", "SP_ROOM" are temperatures in 0.01 C
        .with_columns(
            pl.when(pl.col("field_name").str.contains_any(["AIR_IN", "SP_ROOM"]))
            .then(0.01)
            .otherwise(1.0)  # Default scaling factor if no cases match
            .alias("scale_factor")
        )
        .sort("reg_split", "address")
    )

    result: List[MqttTopic] = []
    for name, data in df.group_by("reg_split"):
        reg_split = str(name[0])
        room = REG_ROOM_MAPPING[reg_split]
        result.append(
            MqttTopic(
                topic=f"{topic_prefix}/{reg_split}",
                modbus_fields=[
                    Address(
                        modbus_register=d["address"],
                        field_name=d["field_name"],
                        description=d["description"],
                        scale_factor=d["scale_factor"],
                    )
                    for d in data.select(
                        ["address", "field_name", "scale_factor", "description"]
                    ).to_dicts()
                ],
                extra_fields=[
                    LiteralField(field_name="reg_split", value=reg_split),
                    LiteralField(field_name="room", value=room),
                ],
            )
        )

    return result


def load_ac_modbus_unit(excel_path: Path, unit_id: int) -> ModbusUnit:
    df = (
        pl.read_excel(excel_path, sheet_name="AC")
        .select(pl.all().name.to_lowercase())
        .select(pl.all().name.replace(" ", "_"))
    )

    topics = select_nested_ac_topics(df, topic_prefix="termodinamica/ac")
    topics.append(
        load_ac_misc_topic(
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


def load_ac_misc_topic(
    df: pl.DataFrame,
    topic: str,
    register_name_filter: List[str],
    field_name_strip: List[str],
) -> MqttTopic:
    df = (
        df.filter(pl.col("register_name").str.contains_any(register_name_filter))
        .with_columns(
            pl.col("register_name")
            .str.replace("|".join(field_name_strip), "")
            .str.strip_chars()
            .str.to_lowercase()
            .alias("field_name"),
        )
        .with_columns(
            pl.when(
                pl.col("field_name").str.contains_any(
                    ["ac_compressor", "sp_room", "wat", "sea_water_pump"]
                )
            )
            .then(0.01)
            .when(
                pl.col("field_name").str.contains_any(
                    ["current_req_pressure", "engine_box_t_sea_water", "engine_box_p"]
                )
            )
            .then(0.001)
            .otherwise(1.0)  # Default scaling factor if no cases match
            .alias("scale_factor")
        )
    )
    print(f"load flat topic {topic} with {len(df)} registers")
    result: List[Address] = []
    for row in df.iter_rows(named=True):
        result.append(
            Address(
                modbus_register=row["address"],
                field_name=row["field_name"],
                description=row["description"],
                scale_factor=row["scale_factor"],
            )
        )

    return MqttTopic(topic=topic, modbus_fields=result)


if __name__ == "__main__":
    modbus_units = [
        load_ac_modbus_unit(excel_path=EXCEL_PATH, unit_id=32),
    ]

    result_filename = SCRIPTS_FOLDER / "../modbus_bridges.json"
    with open(result_filename, "w", encoding="utf-8") as f:
        json_bytes = TypeAdapter(list[ModbusUnit]).dump_json(modbus_units, indent=2)
        f.write(json_bytes.decode("utf-8"))
