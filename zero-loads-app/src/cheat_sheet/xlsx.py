from itertools import groupby
from pathlib import Path

import xlsxwriter
from xlsxwriter.format import Format
from xlsxwriter.worksheet import Worksheet

from cheat_sheet.build import CheatSheet, ThresholdLevel
from sailpack.max_loads import THRESHOLD_COLUMNS

LOAD_CASE_HEADERS = {
    "number": "LC",
    "section": "Section",
    "calculation_id": "Calculation ID",
    "file_name": "File name",
    "sails": "Sails",
    "sail_area": "Sail area (m²)",
    "max_wind_speed": "Max wind speed (kn)",
    "tws": "TWS (kn)",
    "twa": "TWA (°)",
    "aws": "AWS (kn)",
    "awa": "AWA (°)",
    "bsp": "BSP (kn)",
    "heel": "Heel (°)",
}
PLACEHOLDER_LOAD_CASE_COLUMNS = {"sail_area", "max_wind_speed"}
THRESHOLD_LABELS = {
    "alarm_low": "Lower alarm",
    "warning_low": "Lower warning",
    "warning_high": "Upper warning",
    "alarm_high": "Upper alarm",
}
HEADER_ROWS = 3 + len(THRESHOLD_COLUMNS)
FROZEN_COLUMNS = 5
A4_PAPER = 9

PLACEHOLDER_COLOR = "#E7E6E6"
LEVEL_COLORS = {ThresholdLevel.WARNING: "#FFD966", ThresholdLevel.ALARM: "#F4B084"}


class _Formats:
    def __init__(self, workbook: xlsxwriter.Workbook) -> None:
        header = {"bold": True, "border": 1, "valign": "top", "text_wrap": True}
        cell = {"border": 1}
        self.group = workbook.add_format({**header, "align": "center"})
        self.label = workbook.add_format(header)
        self.placeholder_label = workbook.add_format(
            {**header, "bg_color": PLACEHOLDER_COLOR}
        )
        self.technical_name = workbook.add_format(
            {**cell, "font_size": 8, "font_color": "#595959", "text_wrap": True}
        )
        self.threshold_label = workbook.add_format({**cell, "italic": True})
        self.threshold = workbook.add_format(
            {**cell, "italic": True, "num_format": "0.0"}
        )
        self.text = workbook.add_format(cell)
        self.number = workbook.add_format({**cell, "num_format": "0.0"})
        self.placeholder = workbook.add_format({**cell, "bg_color": PLACEHOLDER_COLOR})
        self.levels = {
            ThresholdLevel.NORMAL: self.number,
            **{
                level: workbook.add_format(
                    {**cell, "num_format": "0.0", "bg_color": color}
                )
                for level, color in LEVEL_COLORS.items()
            },
        }


def write_xlsx(cheat_sheet: CheatSheet, output: Path) -> None:
    with xlsxwriter.Workbook(output) as workbook:
        formats = _Formats(workbook)
        _write_loads(workbook.add_worksheet("Cheat sheet"), cheat_sheet, formats)
        _write_legend(workbook.add_worksheet("Legend"), formats)


def _write_loads(sheet: Worksheet, cheat_sheet: CheatSheet, formats: _Formats) -> None:
    first_variable_column = len(LOAD_CASE_HEADERS)
    label_row, technical_name_row = 1, 2

    for column, (key, header) in enumerate(LOAD_CASE_HEADERS.items()):
        header_format = (
            formats.placeholder_label
            if key in PLACEHOLDER_LOAD_CASE_COLUMNS
            else formats.label
        )
        sheet.merge_range(0, column, technical_name_row, column, header, header_format)
    for offset, threshold in enumerate(THRESHOLD_COLUMNS):
        sheet.merge_range(
            technical_name_row + 1 + offset,
            0,
            technical_name_row + 1 + offset,
            FROZEN_COLUMNS - 1,
            f"{THRESHOLD_LABELS[threshold]} (t)",
            formats.threshold_label,
        )

    indexed_columns = list(enumerate(cheat_sheet.columns, start=first_variable_column))
    for group, group_columns in groupby(
        indexed_columns, key=lambda item: item[1].group
    ):
        positions = [position for position, _ in group_columns]
        if len(positions) > 1:
            sheet.merge_range(0, positions[0], 0, positions[-1], group, formats.group)
        else:
            sheet.write(0, positions[0], group, formats.group)

    for position, column in indexed_columns:
        label_format = (
            formats.placeholder_label if column.is_position else formats.label
        )
        sheet.write(
            label_row, position, f"{column.label} ({column.unit})", label_format
        )
        sheet.write(
            technical_name_row, position, column.technical_name, formats.technical_name
        )
        for offset, threshold in enumerate(THRESHOLD_COLUMNS):
            sheet.write(
                technical_name_row + 1 + offset,
                position,
                getattr(column, threshold),
                formats.threshold,
            )

    for row, load_case in enumerate(
        cheat_sheet.load_cases.iter_rows(named=True), start=HEADER_ROWS
    ):
        for column, key in enumerate(LOAD_CASE_HEADERS):
            if key in PLACEHOLDER_LOAD_CASE_COLUMNS:
                sheet.write_blank(row, column, None, formats.placeholder)
            elif isinstance(load_case[key], float):
                sheet.write_number(row, column, load_case[key], formats.number)
            else:
                sheet.write(row, column, load_case[key], formats.text)
        for position, column in indexed_columns:
            target = load_case[column.technical_name]
            if column.is_position:
                sheet.write_blank(row, position, None, formats.placeholder)
            elif target is None:
                sheet.write_blank(row, position, None, formats.number)
            else:
                sheet.write_number(
                    row,
                    position,
                    target,
                    formats.levels[column.threshold_level(target)],
                )

    sheet.set_row(label_row, 60)
    sheet.set_row(technical_name_row, 36)
    sheet.set_column(0, 0, 5)
    sheet.set_column(1, 1, 9)
    sheet.set_column(2, 3, 30)
    sheet.set_column(4, 4, 14)
    sheet.set_column(5, first_variable_column - 1, 9)
    sheet.set_column(first_variable_column, indexed_columns[-1][0], 12)
    sheet.freeze_panes(HEADER_ROWS, FROZEN_COLUMNS)
    sheet.set_landscape()
    sheet.set_paper(A4_PAPER)
    sheet.fit_to_pages(0, 1)
    sheet.repeat_rows(0, HEADER_ROWS - 1)
    sheet.repeat_columns(0, FROZEN_COLUMNS - 1)


def _write_legend(sheet: Worksheet, formats: _Formats) -> None:
    legend: list[tuple[Format, str]] = [
        (
            formats.levels[ThresholdLevel.WARNING],
            "Target above the upper or below the lower warning",
        ),
        (
            formats.levels[ThresholdLevel.ALARM],
            "Target above the upper or below the lower alarm",
        ),
        (formats.placeholder, "Placeholder, to be filled in by hand"),
    ]
    sheet.write(0, 0, "Legend", formats.label)
    for row, (cell_format, description) in enumerate(legend, start=1):
        sheet.write_blank(row, 0, None, cell_format)
        sheet.write(row, 1, description)
    sheet.write(
        len(legend) + 2,
        0,
        "Targets are the raw SailPack loads on port tack (PT is windward), in tonnes; "
        "the starboard tack is the PT/SB mirror.",
    )
    sheet.set_column(0, 0, 6)
    sheet.set_column(1, 1, 70)
