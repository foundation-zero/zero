import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pypdfium2 as pdfium
from matplotlib.axes import Axes
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from PIL import Image, ImageDraw

from cheat_sheet.build import CheatSheet, Column, ThresholdLevel
from cheat_sheet.xlsx import LEVEL_COLORS, PLACEHOLDER_COLOR
from sailpack.export_load_case_mapping_seed import AWA_RANGES, AWS_RANGES

A4_PORTRAIT = (8.27, 11.69)
A4_LANDSCAPE = (11.69, 8.27)
BOOKLET_COLOR = "#2c5a6b"
MUTED_TEXT_COLOR = "#595959"

# The booklet ("Project Zero - PZ - Sail Plan Rig load Guide v6") load case that draws each
# sail set. Its J is the blade, MH0 the code zero, TSL the trisail; it has no A3 drawing.
BOOKLET_LOAD_CASES = {
    frozenset({"B", "FM", "FMZ"}): 1,
    frozenset({"B", "FM", "MZ1R"}): 2,
    frozenset({"B", "FM"}): 5,
    frozenset({"B", "M1R", "MZ1R"}): 6,
    frozenset({"B", "M1R"}): 7,
    frozenset({"B", "M1R", "MZ2R"}): 10,
    frozenset({"SS", "M1R", "MZ1R"}): 11,
    frozenset({"SS", "M1R", "MZ2R"}): 12,
    frozenset({"SS", "M2R", "MZ2R"}): 13,
    frozenset({"SS", "M1R"}): 14,
    frozenset({"SS", "M2R"}): 15,
    frozenset({"SJ", "M2R"}): 16,
    frozenset({"SJ", "M3R"}): 17,
    frozenset({"SJ"}): 19,
    frozenset({"M3R"}): 20,
    frozenset({"FM", "FMZ"}): 21,
    frozenset({"TS"}): 25,
    frozenset({"C0", "FM", "FMZ"}): 32,
    frozenset({"B", "FM", "FMZ", "MZSS"}): 38,
    frozenset({"B", "FM", "FMZ", "MZJ"}): 40,
}

# Fractions of the booklet page height and width around the sail plan drawing, and the boxes
# around the conditions panel and review notes that reach into it.
DRAWING_TOP, DRAWING_BOTTOM = 0.16, 0.70
DRAWING_MASKS = [(0.69, 1.0, 0.0, 0.225), (0.0, 0.27, 0.0, 0.195)]
DRAWING_RENDER_SCALE = 3

LEFT_GROUPS = ["Main mast", "Main sail", "Blade", "Staysail"]

HEADSAIL_CATEGORIES = {
    "B": "Blade",
    "SS": "Staysail",
    "SJ": "Storm jib",
    "C0": "Code zero",
    "A3": "A3",
    "TS": "Trisail",
}
NO_HEADSAIL_CATEGORY = "No headsail"
CATEGORY_COLORS = [
    "#2a78d6",
    "#eb6834",
    "#1baf7a",
    "#eda100",
    "#e87ba4",
    "#008300",
    "#6250d6",
]
CATEGORY_MARKERS = ["o", "s", "^", "D", "v", "P", "X"]


@dataclass(frozen=True)
class TableRow:
    column: Column
    position: Column | None

    @property
    def load(self) -> Column | None:
        return None if self.column.is_position else self.column


def booklet_drawings(
    booklet: Path, sail_sets: Iterable[frozenset[str]]
) -> dict[frozenset[str], Image.Image]:
    document = pdfium.PdfDocument(booklet)
    pages_by_load_case = {
        int(match.group(1)): page
        for page in document
        if (
            match := re.search(
                r"Load Case (\d+)", page.get_textpage().get_text_bounded()
            )
        )
    }
    return {
        sail_set: _crop_drawing(pages_by_load_case[BOOKLET_LOAD_CASES[sail_set]])
        for sail_set in set(sail_sets)
        if sail_set in BOOKLET_LOAD_CASES
    }


def _crop_drawing(page: pdfium.PdfPage) -> Image.Image:
    _, height = page.get_size()
    image = page.render(
        scale=DRAWING_RENDER_SCALE,
        crop=(0, height * (1 - DRAWING_BOTTOM), 0, height * DRAWING_TOP),
    ).to_pil()
    page_height = image.height / (DRAWING_BOTTOM - DRAWING_TOP)
    draw = ImageDraw.Draw(image)
    for left, right, top, bottom in DRAWING_MASKS:
        draw.rectangle(
            (
                left * image.width,
                (top - DRAWING_TOP) * page_height,
                right * image.width,
                (bottom - DRAWING_TOP) * page_height,
            ),
            fill="white",
        )
    return image


def _position_name(load: Column) -> str:
    return f"{load.technical_name.removesuffix('-load')}-relative-position"


def table_rows(columns: list[Column]) -> list[TableRow]:
    """Pair every load with its relative position, keeping positions without a load as rows."""
    by_name = {column.technical_name: column for column in columns}
    paired_positions = {
        _position_name(column) for column in columns if not column.is_position
    }
    return [
        TableRow(
            column=column,
            position=None
            if column.is_position
            else by_name.get(_position_name(column)),
        )
        for column in columns
        if column.technical_name not in paired_positions
    ]


def headsail_category(sails: str) -> str:
    abbreviations = sails.split()
    return next(
        (
            name
            for abbreviation, name in HEADSAIL_CATEGORIES.items()
            if abbreviation in abbreviations
        ),
        NO_HEADSAIL_CATEGORY,
    )


def write_pdf(cheat_sheet: CheatSheet, booklet: Path, output: Path) -> None:
    load_cases = list(cheat_sheet.load_cases.iter_rows(named=True))
    drawings = booklet_drawings(
        booklet, (frozenset(load_case["sails"].split()) for load_case in load_cases)
    )
    with PdfPages(output) as pdf:
        pdf.savefig(_coverage_page(load_cases))
        for load_case in load_cases:
            figure = _load_case_page(
                load_case,
                cheat_sheet.columns,
                drawings.get(frozenset(load_case["sails"].split())),
            )
            pdf.savefig(figure)
            plt.close(figure)


def _load_case_page(
    load_case: dict[str, Any], columns: list[Column], drawing: Image.Image | None
) -> Figure:
    figure = plt.figure(figsize=A4_PORTRAIT)
    figure.text(
        0.06,
        0.95,
        f"Load Case {load_case['number']} - {load_case['section'].upper()}",
        fontsize=22,
        color=BOOKLET_COLOR,
    )
    figure.text(
        0.06, 0.925, f"Sails: {load_case['sails']}", fontsize=11, color=BOOKLET_COLOR
    )
    figure.text(0.06, 0.905, "Max wind speed: – kn", fontsize=9, color=MUTED_TEXT_COLOR)
    figure.text(
        0.06,
        0.885,
        f"Calculation ID: {load_case['calculation_id']}",
        fontsize=7,
        color=MUTED_TEXT_COLOR,
    )
    figure.text(
        0.06,
        0.87,
        f"File: {load_case['file_name']}",
        fontsize=7,
        color=MUTED_TEXT_COLOR,
    )
    _draw_conditions(figure, load_case)

    drawing_axes = figure.add_axes((0.08, 0.47, 0.84, 0.39))
    drawing_axes.set_axis_off()
    if drawing is None:
        drawing_axes.text(
            0.5,
            0.5,
            "No booklet drawing for this sail set",
            ha="center",
            va="center",
            color=MUTED_TEXT_COLOR,
        )
    else:
        drawing_axes.imshow(drawing)

    rows = table_rows(columns)
    _draw_table(
        figure,
        [row for row in rows if row.column.group in LEFT_GROUPS],
        load_case,
        left=0.05,
        right=0.49,
    )
    _draw_table(
        figure,
        [row for row in rows if row.column.group not in LEFT_GROUPS],
        load_case,
        left=0.51,
        right=0.95,
    )
    figure.text(
        0.95,
        0.015,
        f"Port tack SailPack targets in tonnes · generated {date.today().isoformat()}",
        fontsize=6,
        color=MUTED_TEXT_COLOR,
        ha="right",
    )
    return figure


def _draw_conditions(figure: Figure, load_case: dict[str, Any]) -> None:
    left, bottom, width, height = 0.66, 0.84, 0.28, 0.14
    figure.add_artist(
        Rectangle(
            (left, bottom),
            width,
            height,
            transform=figure.transFigure,
            color=BOOKLET_COLOR,
        )
    )
    conditions = [
        ("Sail area", "– m²"),
        ("Heel", f"{load_case['heel']:.0f}°"),
        ("TWS", f"{load_case['tws']:.1f} kn"),
        ("TWA", f"{load_case['twa']:.0f}°"),
        ("AWS", f"{load_case['aws']:.1f} kn"),
        ("AWA", f"{load_case['awa']:.0f}°"),
        ("BSP", f"{load_case['bsp']:.1f} kn"),
    ]
    line_height = height / (len(conditions) + 1)
    for index, (name, value) in enumerate(conditions):
        y = bottom + height - (index + 1) * line_height
        figure.text(left + 0.02, y, name, color="white", fontsize=8, weight="bold")
        figure.text(left + 0.13, y, value, color="white", fontsize=8)


TABLE_TOP = 0.45
TABLE_ROW_HEIGHT = 0.0122
TABLE_COLUMNS = {"LOAD (t)": 0.52, "POS (%)": 0.68, "WARN (t)": 0.84, "MAX (t)": 1.0}
TABLE_CELL_WIDTH = 0.12


def _draw_table(
    figure: Figure,
    rows: list[TableRow],
    load_case: dict[str, Any],
    left: float,
    right: float,
) -> None:
    width = right - left

    def x(fraction: float) -> float:
        return left + fraction * width

    def cell(fraction: float, y: float, color: str) -> None:
        figure.add_artist(
            Rectangle(
                (x(fraction) - TABLE_CELL_WIDTH * width, y - 0.25 * TABLE_ROW_HEIGHT),
                TABLE_CELL_WIDTH * width,
                TABLE_ROW_HEIGHT * 0.95,
                transform=figure.transFigure,
                color=color,
            )
        )

    def number(value: float | None) -> str:
        return "–" if value is None else f"{value:.1f}"

    for name, fraction in TABLE_COLUMNS.items():
        figure.text(
            x(fraction), TABLE_TOP, name, fontsize=6.5, weight="bold", ha="right"
        )

    line = 1
    previous_group = None
    for row in rows:
        if row.column.group != previous_group:
            figure.text(
                x(0),
                TABLE_TOP - line * TABLE_ROW_HEIGHT,
                row.column.group.upper(),
                fontsize=7,
                weight="bold",
                color=BOOKLET_COLOR,
            )
            line += 1
            previous_group = row.column.group
        y = TABLE_TOP - line * TABLE_ROW_HEIGHT

        figure.text(x(0.01), y, row.column.label, fontsize=6.5)

        target = None if row.load is None else load_case[row.load.technical_name]
        if row.load is not None:
            level = row.load.threshold_level(target)
            if level != ThresholdLevel.NORMAL:
                cell(TABLE_COLUMNS["LOAD (t)"], y, LEVEL_COLORS[level])
        if row.position is not None or row.load is None:
            cell(TABLE_COLUMNS["POS (%)"], y, PLACEHOLDER_COLOR)

        values = {
            "LOAD (t)": "" if row.load is None else number(target),
            "POS (%)": "" if row.position is None and row.load is not None else "–",
            "WARN (t)": "" if row.load is None else number(row.load.warning_high),
            "MAX (t)": "" if row.load is None else number(row.load.alarm_high),
        }
        for name, fraction in TABLE_COLUMNS.items():
            figure.text(x(fraction), y, values[name], fontsize=6.5, ha="right")
        line += 1


def _coverage_page(load_cases: list[dict[str, Any]]) -> Figure:
    figure, (apparent_axes, true_axes) = plt.subplots(1, 2, figsize=A4_LANDSCAPE)
    figure.suptitle(
        "Load case coverage", x=0.06, ha="left", fontsize=18, color=BOOKLET_COLOR
    )
    categories = [*HEADSAIL_CATEGORIES.values(), NO_HEADSAIL_CATEGORY]

    for axes, angle, speed, title in [
        (apparent_axes, "awa", "aws", "Apparent wind"),
        (true_axes, "twa", "tws", "True wind"),
    ]:
        for index, category in enumerate(categories):
            category_cases = [
                load_case
                for load_case in load_cases
                if headsail_category(load_case["sails"]) == category
            ]
            if not category_cases:
                continue
            axes.scatter(
                [load_case[angle] for load_case in category_cases],
                [load_case[speed] for load_case in category_cases],
                s=48,
                color=CATEGORY_COLORS[index],
                marker=CATEGORY_MARKERS[index],
                edgecolors="white",
                linewidths=1,
                label=category,
                zorder=3,
            )
        numbers_by_point: dict[tuple[float, float], list[str]] = {}
        for load_case in load_cases:
            numbers_by_point.setdefault(
                (load_case[angle], load_case[speed]), []
            ).append(str(load_case["number"]))
        for point, numbers in numbers_by_point.items():
            axes.annotate(
                ", ".join(numbers),
                point,
                xytext=(5, 3),
                textcoords="offset points",
                fontsize=7,
                color=MUTED_TEXT_COLOR,
            )
        _style_coverage_axes(axes, title, angle.upper(), speed.upper())

    _draw_mapping_ranges(apparent_axes)
    apparent_axes.legend(title="Headsail", fontsize=8, title_fontsize=8, frameon=False)
    figure.text(
        0.06,
        0.02,
        "Numbers are the load case numbers. On the apparent wind plot the shaded bands are the "
        "AWA sections and the dashed lines the AWS ranges of the load case mapping.",
        fontsize=8,
        color=MUTED_TEXT_COLOR,
    )
    return figure


def _style_coverage_axes(axes: Axes, title: str, angle: str, speed: str) -> None:
    axes.set_title(title, loc="left", fontsize=11)
    axes.set_xlabel(f"{angle} (°)")
    axes.set_ylabel(f"{speed} (kn)")
    axes.set_xlim(0, 180)
    axes.set_ylim(0, 60)
    axes.set_xticks(range(0, 181, 20))
    axes.grid(color="#e5e5e5", linewidth=0.6)
    axes.set_axisbelow(True)
    for spine in ["top", "right"]:
        axes.spines[spine].set_visible(False)


def _draw_mapping_ranges(axes: Axes) -> None:
    for index, (section, (lower, upper)) in enumerate(AWA_RANGES.items()):
        axes.axvspan(
            lower, upper, color="#f2f2f2" if index % 2 == 0 else "white", zorder=0
        )
        axes.text(
            (lower + upper) / 2,
            1,
            section,
            ha="center",
            fontsize=8,
            color=MUTED_TEXT_COLOR,
        )
    for lower, _ in AWS_RANGES[1:]:
        axes.axhline(lower, color="#bfbfbf", linestyle="--", linewidth=0.6, zorder=1)
