import csv
import io
from dataclasses import dataclass

import requests

from loads.registry.registry import VARIABLES
from loads.util import camel_to_kebab
from sailpack.max_loads import (
    THRESHOLD_COLUMNS,
    kilogram_to_tonne,
    read_max_loads,
    read_max_loads_cells,
)
from sailpack.seed_utils import missing_purchases, read_reference_values_mapping

LOADS_SHEET_ID = "11sE_LaWqBz4rfQrQgS-j8XIEl9pCgsJEX_HSi0XDoxw"
LOADS_SHEET_EXPORT_URL = f"https://docs.google.com/spreadsheets/d/{LOADS_SHEET_ID}/export?format=csv&gid={{gid}}"

SAILPACK_MAPPING_GID = 1005053580
MAX_LOADS_GID = 321612479

SAILPACK_MAPPING_HEADER_ROWS = 1

SAIL_SYSTEM_TOPIC_PREFIX = "sail-systems/"
# The PLC reference of the loads that do not come from the sail system PLC, such as the fiber optics.
NOT_FROM_THE_PLC = "n/a"


def download_tab(gid: int) -> str:
    response = requests.get(LOADS_SHEET_EXPORT_URL.format(gid=gid), timeout=30)
    response.raise_for_status()
    return response.content.decode("utf-8")


@dataclass(frozen=True)
class LoadsSheet:
    """The CSV exports of the loads Google Sheet tabs."""

    sailpack_mapping: str
    max_loads: str

    @classmethod
    def download(cls) -> "LoadsSheet":
        return cls(
            sailpack_mapping=download_tab(SAILPACK_MAPPING_GID),
            max_loads=download_tab(MAX_LOADS_GID),
        )


def csv_rows(csv_text: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(csv_text, newline="")))


def first_column_values(csv_text: str, header_rows: int) -> set[str]:
    return {
        row[0].strip()
        for row in csv_rows(csv_text)[header_rows:]
        if row and row[0].strip()
    }


def max_loads_technical_names(max_loads_csv: str) -> set[str]:
    try:
        cells_by_row = read_max_loads_cells(max_loads_csv)
    except ValueError:
        # max_loads_problems reports the missing columns.
        return set()
    return {cells["variable"] for cells in cells_by_row}


# TODO: Remove "Set at Docktune Load??" once the mast compression lower warnings are set in the max loads sheet.
MAX_LOADS_PLACEHOLDERS = {"", "???", "n/a", "Not Required", "Set at Docktune Load??"}


def max_loads_problems(max_loads_csv: str) -> list[str]:
    try:
        cells_by_row = read_max_loads_cells(max_loads_csv)
    except ValueError as e:
        return [str(e)]

    non_numeric = [
        f"Max loads: {cells['variable']} has a non-numeric {column}: {cells[column]!r}"
        for cells in cells_by_row
        for column in THRESHOLD_COLUMNS
        if cells[column] not in MAX_LOADS_PLACEHOLDERS
        and kilogram_to_tonne(cells[column]) is None
    ]

    try:
        read_max_loads(max_loads_csv)
    except ValueError as e:
        return [*non_numeric, str(e)]
    return non_numeric


def plc_reference_to_mqtt_key(plc_reference: str) -> str:
    """Convert a PLC reference, such as `FE205_MainSheetCaptiveWinch.st_Load.i_Load`, to the
    adapter's MQTT topic and payload key, such as
    `sail-systems/fe205-main-sheet-captive-winch/st_Load/i_Load`."""
    function_block, _, payload_path = plc_reference.partition(".")
    code, _, name = function_block.rpartition("_")
    topic_segment = (
        f"{code.lower()}-{camel_to_kebab(name)}" if code else camel_to_kebab(name)
    )
    return f"{SAIL_SYSTEM_TOPIC_PREFIX}{topic_segment}/{payload_path.replace('.', '/')}"


def plc_reference_problems(max_loads_csv: str) -> list[str]:
    """Compare the PLC references with the registry, ignoring case, as the sheet's casing differs
    from what the PLC publishes."""
    try:
        cells_by_row = read_max_loads_cells(max_loads_csv)
    except ValueError:
        # max_loads_problems reports the missing columns.
        return []

    plc_rows = [
        (
            cells["variable"],
            cells["plc_reference"],
            f"{variable.topic}/{variable.payload_key}",
        )
        for cells in cells_by_row
        if (variable := VARIABLES.get(cells["variable"]))
        and cells["plc_reference"] != NOT_FROM_THE_PLC
    ]
    unreferenced = [
        f"Max loads: {name} has no PLC reference"
        for name, plc_reference, _ in plc_rows
        if not plc_reference
    ]
    mismatched = [
        f"Max loads: {name} reads {registry_key} in the registry, "
        f"but its PLC reference {plc_reference} is {plc_reference_to_mqtt_key(plc_reference)}"
        for name, plc_reference, registry_key in plc_rows
        if plc_reference
        and plc_reference_to_mqtt_key(plc_reference).casefold()
        != registry_key.casefold()
    ]
    return [*unreferenced, *mismatched]


def sailpack_mapping_problems(mapping_csv: str) -> list[str]:
    try:
        mapping = read_reference_values_mapping(mapping_csv)
    except ValueError as e:
        return [f"SailPack mapping: {e}"]
    return [
        f"SailPack mapping: {load} has no numeric purchase"
        for load in missing_purchases(mapping)
    ]


def consistency_problems(sheet: LoadsSheet) -> list[str]:
    technical_names_by_tab = {
        "SailPack mapping": first_column_values(
            sheet.sailpack_mapping, SAILPACK_MAPPING_HEADER_ROWS
        ),
        "Max loads": max_loads_technical_names(sheet.max_loads),
    }
    unknown_names = [
        f"{tab_name}: technical names not in the registry: {sorted(unknown)}"
        for tab_name, names in technical_names_by_tab.items()
        if (unknown := names - VARIABLES.keys())
    ]
    return [
        *unknown_names,
        *max_loads_problems(sheet.max_loads),
        *plc_reference_problems(sheet.max_loads),
        *sailpack_mapping_problems(sheet.sailpack_mapping),
    ]
