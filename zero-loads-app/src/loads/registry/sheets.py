import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import requests

from loads.registry.registry import VARIABLES

LOADS_SHEET_ID = "11sE_LaWqBz4rfQrQgS-j8XIEl9pCgsJEX_HSi0XDoxw"
LOADS_SHEET_EXPORT_URL = f"https://docs.google.com/spreadsheets/d/{LOADS_SHEET_ID}/export?format=csv&gid={{gid}}"

SRC = Path(__file__).parents[2]

TabName = Literal["sailpack-mapping", "max-loads", "vitters-io-list"]


@dataclass(frozen=True)
class SheetTab:
    gid: int
    path: Path
    header_rows: int


TABS: dict[TabName, SheetTab] = {
    "sailpack-mapping": SheetTab(
        gid=1005053580, path=SRC / "sailpack" / "sailpack_mapping.csv", header_rows=1
    ),
    "max-loads": SheetTab(
        gid=321612479, path=SRC / "loads" / "registry" / "max_loads.csv", header_rows=2
    ),
    "vitters-io-list": SheetTab(
        gid=1801629266,
        path=SRC / "loads" / "registry" / "vitters_io_list.csv",
        header_rows=2,
    ),
}

VITTERS_JOIN_PATH = SRC / "loads" / "registry" / "vitters_join.csv"


def download_tab(tab: SheetTab) -> None:
    response = requests.get(LOADS_SHEET_EXPORT_URL.format(gid=tab.gid), timeout=30)
    response.raise_for_status()
    tab.path.write_bytes(response.content)


def _rows(path: Path, header_rows: int) -> list[list[str]]:
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.reader(file))[header_rows:]


def unknown_technical_names(path: Path, header_rows: int) -> set[str]:
    names = {
        row[0].strip() for row in _rows(path, header_rows) if row and row[0].strip()
    }
    return names - VARIABLES.keys()


def unresolved_vitters_joins() -> list[tuple[str, str, str]]:
    io_list_tab = TABS["vitters-io-list"]
    io_list = {
        (row[0], row[1])
        for row in _rows(io_list_tab.path, io_list_tab.header_rows)
        if row
    }
    return [
        (name, kind, address)
        for name, kind, address in _rows(VITTERS_JOIN_PATH, header_rows=1)
        if (kind, address) not in io_list
    ]


MAX_LOADS_PLACEHOLDERS = {"", "???", "n/a"}


def max_loads_problems() -> list[str]:
    from sailpack.max_loads import (
        ALARM_SETTING_COLUMN,
        TECHNICAL_NAME_COLUMN,
        WARNING_THRESHOLD_COLUMN,
        read_max_loads,
    )

    max_loads_tab = TABS["max-loads"]
    non_numeric = [
        f"{max_loads_tab.path.name}: {row[TECHNICAL_NAME_COLUMN]} has a non-numeric threshold: {row[column]!r}"
        for row in _rows(max_loads_tab.path, max_loads_tab.header_rows)
        if row and row[TECHNICAL_NAME_COLUMN].strip()
        for column in (WARNING_THRESHOLD_COLUMN, ALARM_SETTING_COLUMN)
        if row[column].strip() not in MAX_LOADS_PLACEHOLDERS
        and not row[column].replace(",", "").strip().replace(".", "", 1).isdigit()
    ]

    try:
        read_max_loads(max_loads_tab.path)
    except ValueError as e:
        return [*non_numeric, str(e)]
    return non_numeric


def consistency_problems() -> list[str]:
    technical_name_files = [
        (TABS["sailpack-mapping"].path, TABS["sailpack-mapping"].header_rows),
        (TABS["max-loads"].path, TABS["max-loads"].header_rows),
        (VITTERS_JOIN_PATH, 1),
    ]
    unknown_names = [
        f"{path.name}: technical names not in the registry: {sorted(names)}"
        for path, header_rows in technical_name_files
        if (names := unknown_technical_names(path, header_rows))
    ]
    unresolved_joins = [
        f"{VITTERS_JOIN_PATH.name}: {name} ({kind} {address}) not in the Vitters IO list"
        for name, kind, address in unresolved_vitters_joins()
    ]
    return [*unknown_names, *unresolved_joins, *max_loads_problems()]
