import csv
import io
from dataclasses import dataclass

import requests

from loads.registry.registry import VARIABLES
from sailpack.max_loads import (
    THRESHOLD_COLUMNS,
    kilogram_to_tonne,
    read_max_loads,
    read_max_loads_cells,
)

LOADS_SHEET_ID = "11sE_LaWqBz4rfQrQgS-j8XIEl9pCgsJEX_HSi0XDoxw"
LOADS_SHEET_EXPORT_URL = f"https://docs.google.com/spreadsheets/d/{LOADS_SHEET_ID}/export?format=csv&gid={{gid}}"

SAILPACK_MAPPING_GID = 1005053580
MAX_LOADS_GID = 321612479

SAILPACK_MAPPING_HEADER_ROWS = 1


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
    ]
