import csv
from dataclasses import dataclass
from pathlib import Path

MACROS_DIR = Path(__file__).resolve().parents[2] / "dbt" / "macros"
DEVICE_METADATA_CSV = MACROS_DIR / "marpower_device_metadata.csv"
DEVICE_METADATA_MACRO = MACROS_DIR / "load_marpower_device_metadata.sql"

COLUMNS = ("topic", "system", "kind", "technical_name", "yard_tag", "name")

MACRO_TEMPLATE = """\
/*
 * Generated from marpower_device_metadata.csv by `just generate-device-metadata`; edit the CSV.
 *
 * Devices on the Marpower topic convention (marpower/<NN>-<system>/<kind>[/<instance>]), one row per
 * topic, with the device's yard tag and functional name. Created by a macro for the same reason as
 * load_power_tag_metadata: Greptime needs a time index, which dbt seeds don't give.
 */

{{% macro load_marpower_device_metadata() %}}

    {{% set target_table = 'marpower__device_metadata' %}}

    {{% set query %}}
        DROP TABLE IF EXISTS {{{{ target_table }}}};

        CREATE TABLE {{{{ target_table }}}} (
            ts TIMESTAMP,
            topic STRING,
            "system" STRING,
            kind STRING,
            technical_name STRING,
            yard_tag STRING,
            "name" STRING,
            TIME INDEX (ts),
            PRIMARY KEY (topic)
        );

        INSERT INTO {{{{ target_table }}}} (ts, topic, "system", kind, technical_name, yard_tag, "name")
        VALUES
{values};
    {{% endset %}}

    {{% do log("Create Marpower device metadata table and insert data...", info=True) %}}
    {{% do run_query(query) %}}
    {{% do log("Success! Data has been loaded.", info=True) %}}

{{% endmacro %}}
"""


@dataclass(frozen=True)
class Device:
    topic: str
    system: str
    kind: str
    technical_name: str
    yard_tag: str | None
    name: str | None


def read_devices(csv_file: Path = DEVICE_METADATA_CSV) -> list[Device]:
    with csv_file.open(newline="") as f:
        return [
            Device(
                topic=row["topic"],
                system=row["system"],
                kind=row["kind"],
                technical_name=row["technical_name"],
                yard_tag=row["yard_tag"] or None,
                name=row["name"] or None,
            )
            for row in csv.DictReader(f)
        ]


def _sql_literal(value: str | None) -> str:
    if value is None:
        return "NULL"
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


def render_macro(devices: list[Device]) -> str:
    values = ",\n".join(
        "            ('1970-01-01 00:00:00', "
        + ", ".join(_sql_literal(getattr(device, column)) for column in COLUMNS)
        + ")"
        for device in devices
    )
    return MACRO_TEMPLATE.format(values=values)


def generate_device_metadata(
    csv_file: Path = DEVICE_METADATA_CSV, macro_file: Path = DEVICE_METADATA_MACRO
) -> None:
    macro_file.write_text(render_macro(read_devices(csv_file)))
