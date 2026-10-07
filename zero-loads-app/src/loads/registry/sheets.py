import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import requests

from loads.registry.registry import VARIABLES, VariableDefinition

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

# IO list topics with a display name that the loads app does not read (yet).
IO_LIST_TOPICS_NOT_IN_REGISTRY = {
    # The PLC does not publish these on MQTT yet; the registry reads st_Load instead.
    "F0201_MainOuthaul.st_loadLc.i_Load",
    "F0501_MizzenOuthaul.st_loadLc.i_Load",
    "FE205_MainSheetCaptiveWinch.i_sheetLoad",
    # Not shown in the loads app.
    "FE106_AnchorWindlassPs.i_ChainLength",
    "FE107_AnchorWindlassSb.i_ChainLength",
    "F0202_MainVang.st_loadBottom.i_Load",
    "F0202_MainVang.st_loadRod.i_Load",
    "F0502_MizzenVang.st_loadBottom.i_Load",
    "F0502_MizzenVang.st_loadRod.i_Load",
    # TODO: Add the captive winch positions to the registry.
    "FE201_BladeSheetCaptiveWinchPs.i_PositionPermille",
    "FE203_StaysailSheetCaptiveWinchPs.i_PositionPermille",
    "FE205_MainSheetCaptiveWinch.i_PositionPermille",
    "FE207_MainHalyardCaptiveWinch.i_PositionPermille",
    "FE301_BladeSheetCaptiveWinchSb.i_PositionPermille",
    "FE303_StaysailSheetCaptiveWinchSb.i_PositionPermille",
    "FE401_MainRunnerCaptiveWinchPs.i_PositionPermille",
    "FE402_MizzenRunnerCaptiveWinchPs.i_PositionPermille",
    "FE404_MizzenHalyardCaptiveWinch.i_PositionPermille",
    "FE501_MainRunnerCaptiveWinchSb.i_PositionPermille",
    "FE502_MizzenRunnerCaptiveWinchSb.i_PositionPermille",
    "FE504_MizzenSheetCaptiveWinch.i_PositionPermille",
}


@dataclass(frozen=True)
class IoListLabel:
    display_name: str
    abbreviated_display_name: str
    display_units: str


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


def _normalized_function_block(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _io_list_key(io_list_topic: str) -> str:
    function_block, _, path = io_list_topic.partition(".")
    return f"{_normalized_function_block(function_block)}.{path.lower()}"


def _variable_io_list_key(variable: VariableDefinition) -> str:
    # MQTT topics are the kebab-cased PLC function blocks; the PLC ignores case.
    function_block = variable.topic.removeprefix("sail-systems/")
    path = variable.payload_path.replace("/", ".").lower()
    return f"{_normalized_function_block(function_block)}.{path}"


def _io_list_labels_by_topic() -> dict[str, IoListLabel]:
    io_list_tab = TABS["vitters-io-list"]
    with io_list_tab.path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.reader(file))

    headers = [" ".join(header.split()) for header in rows[io_list_tab.header_rows - 1]]
    topic, display_name, abbreviated_display_name, display_units = (
        headers.index(header)
        for header in [
            "Topic",
            "Display name",
            "Abbreviated display name",
            "Display units",
        ]
    )
    return {
        row[topic].strip(): IoListLabel(
            display_name=row[display_name].strip(),
            abbreviated_display_name=row[abbreviated_display_name].strip(),
            display_units=row[display_units].strip(),
        )
        for row in rows[io_list_tab.header_rows :]
        if row and row[display_name].strip()
    }


def io_list_labels() -> dict[str, IoListLabel]:
    """Return the Vitters IO list labels by technical name, joined on the IO list topic."""
    variable_ids_by_key = {
        _variable_io_list_key(variable): variable.id for variable in VARIABLES.values()
    }
    return {
        variable_ids_by_key[_io_list_key(topic)]: label
        for topic, label in _io_list_labels_by_topic().items()
        if _io_list_key(topic) in variable_ids_by_key
    }


def io_list_topics_without_variable() -> list[str]:
    variable_keys = {_variable_io_list_key(variable) for variable in VARIABLES.values()}
    return sorted(
        topic
        for topic in _io_list_labels_by_topic()
        if _io_list_key(topic) not in variable_keys
        and topic not in IO_LIST_TOPICS_NOT_IN_REGISTRY
    )


def stale_io_list_exceptions() -> list[str]:
    variable_keys = {_variable_io_list_key(variable) for variable in VARIABLES.values()}
    labelled_topics = _io_list_labels_by_topic()
    return sorted(
        topic
        for topic in IO_LIST_TOPICS_NOT_IN_REGISTRY
        if topic not in labelled_topics or _io_list_key(topic) in variable_keys
    )


# TODO: Remove "Set at Docktune Load??" once the mast compression lower warnings are set in the max loads sheet.
MAX_LOADS_PLACEHOLDERS = {"", "???", "n/a", "Not Required", "Set at Docktune Load??"}


def max_loads_problems() -> list[str]:
    from sailpack.max_loads import (
        THRESHOLD_COLUMNS,
        read_max_loads,
        read_max_loads_cells,
    )

    max_loads_path = TABS["max-loads"].path
    try:
        cells_by_row = read_max_loads_cells(max_loads_path)
    except ValueError as e:
        return [str(e)]

    non_numeric = [
        f"{max_loads_path.name}: {cells['variable']} has a non-numeric {column}: {cells[column]!r}"
        for cells in cells_by_row
        for column in THRESHOLD_COLUMNS
        if cells[column] not in MAX_LOADS_PLACEHOLDERS
        and not cells[column].replace(",", "").replace(".", "", 1).isdigit()
    ]

    try:
        read_max_loads(max_loads_path)
    except ValueError as e:
        return [*non_numeric, str(e)]
    return non_numeric


def consistency_problems() -> list[str]:
    technical_name_files = [
        (TABS["sailpack-mapping"].path, TABS["sailpack-mapping"].header_rows),
        (TABS["max-loads"].path, TABS["max-loads"].header_rows),
    ]
    unknown_names = [
        f"{path.name}: technical names not in the registry: {sorted(names)}"
        for path, header_rows in technical_name_files
        if (names := unknown_technical_names(path, header_rows))
    ]
    io_list_name = TABS["vitters-io-list"].path.name
    unmatched_topics = [
        f"{io_list_name}: {topic} has a display name but no registry variable"
        for topic in io_list_topics_without_variable()
    ]
    stale_exceptions = [
        f"{io_list_name}: {topic} is listed as not in the registry but has no display name or is in the registry"
        for topic in stale_io_list_exceptions()
    ]
    return [
        *unknown_names,
        *unmatched_topics,
        *stale_exceptions,
        *max_loads_problems(),
    ]
