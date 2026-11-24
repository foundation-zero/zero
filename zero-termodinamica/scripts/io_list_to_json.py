"""Generate modbus_bridges.json from the Termodinamica Excel file."""

import json
from pathlib import Path

import polars as pl

SCRIPTS_FOLDER = Path(__file__).parent
EXCEL_PATH = SCRIPTS_FOLDER / "../docs/Vent en AC lijst Termodynamica.xls"

# Room per AC unit address, from docs/Termodinamica_Vitters_Wiring
# schematic_REV.11_A.pdf (sheet 1). Some units drive slaves on the same address:
# 8.1 (master cabin stbd), 18.1 (fwd galley) and 23.1-23.3 (main deckhouse).
REG_ROOM_MAPPING = {
    "01": "Tech room",
    "02": "Lounge",
    "03": "Aft stbd guest cabin",
    "04": "Master bathroom stbd",
    "05": "Fwd port guest cabin Fr.55",
    "06": "Aft port guest cabin",
    "07": "Master bathroom port",
    "08": "Master cabin port",
    "09": "Master deckhouse",
    "10": "Office",
    "11": "Port guest cabin Fr.42",
    "12": "Mission room",
    "13": "Laundry",
    "14": "Captain cabin",
    "15": "Mid port crew cabin",
    "16": "Fwd port crew cabin",
    "17": "Watersport storage",
    "18": "Aft galley",
    "19": "Crew mess",
    "20": "Aft stbd crew cabin",
    "21": "Mid-ship stbd crew cabin",
    "22": "Fwd stbd crew cabin",
    "23": "Main deckhouse fwd stbd",
    "24": "Aft area air handler",
    "25": "Aft area extraction",
    "26": "Fwd area air handler",
    "27": "Fwd area extraction",
    "28": "Rack",
    "29": "Navcom",
    "30": "HM10 backup cooling panels",
}


def _ac_topic_dict(
    reg_split: str, room: str, fields: list[dict], topic_prefix: str
) -> dict:
    return {
        "topic": f"{topic_prefix}/{reg_split}",
        "model": "air_conditioning_room",
        "modbus_fields": fields,
        "extra_fields": {"reg_split": reg_split, "room": room},
    }


def select_nested_ac_topics(df: pl.DataFrame, topic_prefix: str) -> list[dict]:
    """Return AC room topic dicts from the Excel frame."""
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
        .with_columns(
            pl.when(
                pl.col("field_name").str.contains_any(
                    ["air_temperature_in", "setpoint_room_temperature"]
                )
            )
            .then(0.01)
            .otherwise(1.0)
            .alias("scale_factor")
        )
        .sort("reg_split", "address")
    )

    result: list[dict] = []
    for name, data in df.group_by("reg_split"):
        reg_split = str(name[0])
        if reg_split not in REG_ROOM_MAPPING:
            continue  # not on the wiring schematic
        room = REG_ROOM_MAPPING[reg_split]
        fields = [
            {
                "modbus_register": d["address"],
                "field_name": d["field_name"],
                "description": d["description"],
                "scale_factor": d["scale_factor"],
            }
            for d in data.select(
                ["address", "field_name", "scale_factor", "description"]
            ).to_dicts()
        ]
        result.append(_ac_topic_dict(reg_split, room, fields, topic_prefix))
    return result


def load_ac_misc_topic(
    df: pl.DataFrame,
    topic: str,
    register_name_filter: list[str],
    field_name_strip: list[str],
) -> dict:
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
            .otherwise(1.0)
            .alias("scale_factor")
        )
    )
    print(f"load flat topic {topic} with {len(df)} registers")
    fields = [
        {
            "modbus_register": row["address"],
            "field_name": row["field_name"],
            "description": row["description"],
            "scale_factor": row["scale_factor"],
        }
        for row in df.iter_rows(named=True)
    ]
    return {"topic": topic, "model": "ac_misc", "modbus_fields": fields}


AC_UNIT_ID = 32
# Two identical DVS bridges of 31 slots each. Only these slots hold an air
# handler: docs/Termodinamica_Vitters_Wiring schematic_REV.11_A.pdf (sheet 2),
# matching the live bridges on 2026-11-24, where the other slots read all zero.
VENTILATION_UNIT_IDS = {"1": 33, "2": 34}
VENTILATION_ROOMS = {
    "1": {
        "02": "Main deckhouse",
        "03": "Office",
        "04": "Galley",
        "05": "Guest Fr.42 port",
        "06": "Guest Fr.38 port",
        "07": "Crew mess",
        "08": "Laundry",
        "09": "Captain cabin",
        "10": "Crew cabin 1",
        "11": "Crew cabin 2",
        "12": "Crew cabin 3",
        "13": "Crew cabin 4",
        "14": "Crew cabin 5",
    },
    "2": {
        "02": "Watersport storage",
        "03": "Lower salon",
        "04": "Guest aft stbd",
        "05": "Day head",
        "06": "Master cabin 1",
        "07": "Master deckhouse",
        "08": "Guest Fr.55 port",
        "09": "Guest aft port",
    },
}
HEAT_PUMP_UNIT_ID = 35
# Each cold room sits on its own slave slot; its block starts at 200 + 10 * (slot - 1).
COLD_ROOM_UNITS = {"fridge": (36, 2), "freezer": (37, 3)}

# The HPB bridge uses the base register map (Fw 8.14.17, see docs/), with the
# heat pump as slave unit 2: slot 1 (200..204) only holds placeholders. It is
# controlled through registers 30 (global on/off) and 10/11/12 (slave
# selection, on/off and set point); 210..214 read the slave back.
HEAT_PUMP_FIELDS = [
    (30, "system_disabled", "Global On/Off System: 1=OFF 0=ON", 1.0),
    (140, "compressor_speed", "Inverter Compressor Speed (0.1 %)", 0.1),
    (141, "water_pump_speed", "Inverter Water Pump Speed (0.1 %)", 0.1),
    (
        182,
        "compressor_power",
        "Compressor absorption (W). The map says 1=0,01 Watt, but live it reads "
        "13 at 0.54 A: 1=10 Watt",
        10.0,
    ),
    (185, "compressor_current", "Compressor absorption (1=0,01 Ampere)", 0.01),
    (190, "active_error", "General Active Error bit field", 1.0),
    (210, "power", "Unit Power On/Off 0=OFF 1=ON", 1.0),
    (
        211,
        "setpoint_temperature",
        "Unit SetPoint (hundredths of degrees Celsius), range 6..70 °C",
        0.01,
    ),
    (213, "temperature", "Unit temperature (hundredths of degrees Celsius)", 0.01),
    (214, "status", "Diagnostic communication status bit field", 1.0),
]


# The fridge and freezer bridges expose the same subset of the base map, with
# signed temperatures (two's complement): fridge 1..20 °C, freezer -5..-20 °C.
# Unlike the heat pump, their slot differs per bridge (see COLD_ROOM_UNITS).
def cold_room_fields(slot: int) -> list[tuple[int, str, str, float]]:
    start = 200 + 10 * (slot - 1)
    return [
        (30, "system_disabled", "Global On/Off System: 1=OFF 0=ON", 1.0),
        (140, "compressor_speed", "Inverter Compressor Speed (0.1 %)", 0.1),
        (
            182,
            "compressor_power",
            "Compressor absorption (W). The map says 1=0,01 Watt, but live it "
            "reads 13 at 0.54 A: 1=10 Watt",
            10.0,
        ),
        (185, "compressor_current", "Compressor absorption (1=0,01 Ampere)", 0.01),
        (190, "active_error", "General Active Error bit field", 1.0),
        (start, "power", "Unit Power On/Off 0=OFF 1=ON", 1.0),
        (
            start + 1,
            "setpoint_temperature",
            "Unit SetPoint (hundredths of degrees Celsius, signed)",
            0.01,
        ),
        (
            start + 3,
            "temperature",
            "Unit temperature (hundredths of degrees Celsius, signed)",
            0.01,
        ),
        (start + 4, "status", "Diagnostic communication status bit field", 1.0),
    ]


def select_ventilation_topics(df: pl.DataFrame, bridge: str) -> list[dict]:
    """Return a topic dict per populated DVS air handler slot on one bridge."""
    df = (
        df.filter(pl.col("register_name").str.contains(r"^REG_SPLIT_\d\d_READ_"))
        .with_columns(
            pl.col("register_name").str.extract(r"REG_SPLIT_(\d+)").alias("unit"),
            pl.col("register_name")
            .str.extract(r"REG_SPLIT_\d+_READ_(.*)", 1)
            .str.to_lowercase()
            .str.replace(r"^sp_(.*?)(_2)?$", "setpoint_$1$2")
            .str.replace(r"humi(_lev)?", "humidity")
            .str.replace("co2_lev", "co2_level")
            .alias("field_name"),
            pl.col("address").cast(pl.Int64),
        )
        .with_columns(
            pl.when(pl.col("field_name").str.contains("humidity"))
            .then(0.1)
            .otherwise(1.0)
            .alias("scale_factor")
        )
        .sort("unit", "address")
    )
    return [
        {
            "topic": f"termodinamica/ventilation/{bridge}/{unit}",
            "model": "ventilation_unit",
            "modbus_fields": [
                {
                    "modbus_register": d["address"],
                    "field_name": d["field_name"],
                    "description": d["description"],
                    "scale_factor": d["scale_factor"],
                }
                for d in data.iter_rows(named=True)
            ],
            "extra_fields": {
                "bridge": bridge,
                "unit": unit,
                "room": VENTILATION_ROOMS[bridge][unit],
            },
        }
        for (unit,), data in df.group_by("unit", maintain_order=True)
        if unit in VENTILATION_ROOMS[bridge]
    ]


def fixed_topic(
    topic: str,
    model: str,
    fields: list[tuple[int, str, str, float]],
    start_register: int | None = None,
) -> dict:
    """Topic dict for a bridge whose registers are listed in this script.

    ``start_register`` places the model's offset fields, such as a slave slot.
    """
    return {
        "topic": topic,
        "model": model,
        **({"start_register": start_register} if start_register is not None else {}),
        "modbus_fields": [
            {
                "modbus_register": register,
                "field_name": field_name,
                "description": description,
                "scale_factor": scale_factor,
            }
            for register, field_name, description, scale_factor in fields
        ],
    }


def _read_sheet(excel_path: Path, sheet_name: str, **kwargs) -> pl.DataFrame:
    return (
        pl.read_excel(excel_path, sheet_name=sheet_name, **kwargs)
        .select(pl.all().name.to_lowercase())
        .select(pl.all().name.replace(" ", "_"))
    )


def load_ac_topics(excel_path: Path) -> list[dict]:
    df = _read_sheet(excel_path, "AC")
    return [
        *select_nested_ac_topics(df, topic_prefix="termodinamica/ac"),
        load_ac_misc_topic(
            df,
            topic="termodinamica/ac-misc",
            register_name_filter=[
                "REG_ABSORPTION_",
                "REG_SPLIT_ENGINE",
                "REG_SPLIT_CURRENT",
            ],
            field_name_strip=["REG_ABSORPTION_", "REG_SPLIT_"],
        ),
    ]


def load_modbus_data(excel_path: Path) -> list[dict]:
    # The Vent sheet has three title rows above its header.
    ventilation_df = _read_sheet(
        excel_path, "Vent", read_options={"header_row": 3}
    ).filter(pl.col("register_name").is_not_null())
    return [
        {"unit_id": AC_UNIT_ID, "topics": load_ac_topics(excel_path)},
        *(
            {
                "unit_id": unit_id,
                "topics": select_ventilation_topics(ventilation_df, bridge),
            }
            for bridge, unit_id in VENTILATION_UNIT_IDS.items()
        ),
        {
            "unit_id": HEAT_PUMP_UNIT_ID,
            "topics": [
                fixed_topic("termodinamica/heat-pump", "heat_pump", HEAT_PUMP_FIELDS)
            ],
        },
        *(
            {
                "unit_id": unit_id,
                "topics": [
                    fixed_topic(
                        f"termodinamica/{room}",
                        "cold_room",
                        cold_room_fields(slot),
                        start_register=200 + 10 * (slot - 1),
                    )
                ],
            }
            for room, (unit_id, slot) in COLD_ROOM_UNITS.items()
        ),
    ]


if __name__ == "__main__":
    modbus_data = load_modbus_data(excel_path=EXCEL_PATH)
    result_filename = SCRIPTS_FOLDER / "../modbus_bridges.json"
    with open(result_filename, "w", encoding="utf-8") as f:
        json.dump(modbus_data, f, indent=2, ensure_ascii=False)
        f.write("\n")
