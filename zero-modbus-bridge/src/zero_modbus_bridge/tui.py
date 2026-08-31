"""Interactive stub TUI: edit Modbus register values in a table.

Development helper for the services that read from Modbus gateways
(``zero-hull-temperature``, ``zero-power-tags``). Hosts the same stub servers as
``Stub`` and renders their register space as an editable, human-scaled table.
"""

import logging
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal, cast

from pydantic import BaseModel
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    TabbedContent,
    TabPane,
)

from zero_modbus_bridge.io import ModbusField, ModbusTopic, extract_modbus_fields
from zero_modbus_bridge.stub import MultiUnitDataHandler, Stub

logger = logging.getLogger(__name__)

type EditableDataType = Literal["uint16", "float32"]


class FieldRow(BaseModel):
    """One editable value rendered as a single table row."""

    unit_id: int
    topic: str
    name: str
    address: int
    data_type: EditableDataType
    scale_factor: float = 1.0
    unit: str | None = None


def _register_of(topic: ModbusTopic, field: ModbusField) -> int:
    if field.offset is not None:
        return topic.start_register + field.offset
    if field.register is not None:
        return field.register
    raise ValueError("ModbusField has neither register nor offset")


def _field_unit(topic: ModbusTopic, name: str) -> str | None:
    field = topic.model.model_fields.get(name)
    if field is None:
        return None
    extra = field.json_schema_extra
    if isinstance(extra, dict):
        unit = extra.get("x-unit")
        return unit if isinstance(unit, str) else None
    return None


def _editable_row(
    topic: ModbusTopic, names: list[str], index: int, field: ModbusField
) -> FieldRow:
    """One editable row; converter-driven fields fall back to the register label.

    Callers must skip coil/bool fields: their ``data_type`` is not representable
    as an ``EditableDataType``, hence the cast below.
    """
    name = names[index] if index < len(names) else ""
    address = _register_of(topic, field)
    return FieldRow(
        unit_id=topic.unit_id,
        topic=topic.topic,
        name=name or str(address),
        address=address,
        data_type=cast(EditableDataType, field.data_type),
        scale_factor=field.scale_factor,
        unit=_field_unit(topic, name) if name else None,
    )


def _topic_rows(topic: ModbusTopic) -> list[FieldRow]:
    """Editable rows for one topic; coil/bool fields are skipped."""
    names = list(extract_modbus_fields(topic.model))
    return [
        _editable_row(topic, names, index, field)
        for index, field in enumerate(topic.fields)
        if field.modbus_type != "coil" and field.data_type != "bool"
    ]


def build_rows(topics: Sequence[ModbusTopic]) -> list[FieldRow]:
    """Flatten a topic group into editable field rows.

    Annotation-driven topics name rows after the model field; converter-driven
    topics fall back to the register address as the label.
    """
    return [row for topic in topics for row in _topic_rows(topic)]


def human_value(handler: MultiUnitDataHandler, row: FieldRow) -> float:
    if row.data_type == "float32":
        return handler.read_float(row.unit_id, row.address) * row.scale_factor
    return handler.read_register(row.unit_id, row.address) * row.scale_factor


def format_value(value: float, data_type: EditableDataType) -> str:
    if data_type == "float32":
        return f"{value:g}"
    return str(round(value))


def write_value(handler: MultiUnitDataHandler, row: FieldRow, text: str) -> None:
    value = float(text) / row.scale_factor
    if row.data_type == "float32":
        handler.set_float(row.unit_id, row.address, value)
        return
    raw = max(0, min(65535, round(value)))
    handler.set_register(row.unit_id, row.address, raw)


@dataclass
class _ServerTab:
    title: str
    handler: MultiUnitDataHandler
    rows: list[FieldRow]


class EditScreen(ModalScreen[str | None]):
    """Modal input for a single field value."""

    BINDINGS = [
        Binding("escape", "dismiss(None)", "Cancel"),
    ]

    def __init__(self, row: FieldRow, current: str):
        super().__init__()
        self._row = row
        self._current = current

    def compose(self) -> ComposeResult:
        unit = f" [{self._row.unit}]" if self._row.unit else ""
        yield Label(
            f"{self._row.topic} — {self._row.name} (reg {self._row.address}{unit})"
        )
        yield Input(value=self._current, id="value")

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)


class StubTui(App):
    """Textual app rendering one tab per stub server."""

    TITLE = "Modbus Stub"
    CSS = """
    #filter {
        margin: 0 1;
        height: 3;
    }
    /* Constrain to the viewport: auto-height would let the table grow past
       the screen, disabling its internal scrolling. */
    TabbedContent {
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("/", "focus_filter", "Filter"),
    ]

    def __init__(self, tabs: list[_ServerTab]):
        super().__init__()
        self._tabs = tabs
        self._filter = ""
        self._editing: tuple[int, int] = (0, 0)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="Filter (/ to focus)", id="filter")
        with TabbedContent():
            for index, tab in enumerate(self._tabs):
                with TabPane(tab.title, id=f"server-{index}"):
                    yield DataTable(id=f"table-{index}")
        yield Footer()

    def on_mount(self) -> None:
        for index, tab in enumerate(self._tabs):
            table = self._table(index)
            table.cursor_type = "row"
            table.add_columns("Unit", "Topic", "Name", "Reg", "Type", "Value", "Unit")
            self._render_tab(index)

    def _table(self, index: int) -> DataTable:
        return self.query_one(f"#table-{index}", DataTable)

    def _active_index(self) -> int:
        content = self.query_one(TabbedContent)
        active = content.active
        if active is None:
            return 0
        return int(active.split("-")[-1])

    def _render_tab(self, index: int) -> None:
        table = self._table(index)
        tab = self._tabs[index]
        table.clear()
        lowered = self._filter.lower()
        for row_index, row in enumerate(tab.rows):
            if lowered and not self._matches(row, lowered):
                continue
            table.add_row(
                str(row.unit_id),
                row.topic,
                row.name,
                str(row.address),
                row.data_type,
                format_value(human_value(tab.handler, row), row.data_type),
                row.unit or "",
                key=str(row_index),
            )

    def _matches(self, row: FieldRow, lowered: str) -> bool:
        searchable_fields = [
            row.topic,
            row.name,
            str(row.address),
            str(row.unit_id),
            row.data_type,
            row.unit or "",
        ]
        return lowered in " ".join(searchable_fields).lower()

    def _edit_row(self, index: int, row_index: int) -> None:
        tab = self._tabs[index]
        row = tab.rows[row_index]
        current = format_value(human_value(tab.handler, row), row.data_type)
        self._editing = (index, row_index)
        self.push_screen(EditScreen(row, current), self._apply_edit)

    def _apply_edit(self, text: str | None) -> None:
        index, row_index = self._editing
        if text is None:
            return
        tab = self._tabs[index]
        row = tab.rows[row_index]
        try:
            write_value(tab.handler, row, text)
        except (ValueError, TypeError):
            self.notify(f"Invalid value: {text!r}", severity="error")
            return
        self._render_tab(index)

    def action_focus_filter(self) -> None:
        self.query_one("#filter", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "filter":
            self._filter = event.value
            self._render_tab(self._active_index())

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.row_key.value is None:
            return
        index = self._active_index()
        self._edit_row(index, int(event.row_key.value))


def run_tui(
    topic_groups: Sequence[tuple[Sequence[ModbusTopic], int]],
    bind_host: str = "0.0.0.0",
    default_value: int = 0,
    float_default: float | None = None,
) -> None:
    """Start the stub servers and run the interactive TUI until quit."""
    stub = Stub.from_topic_groups(
        list(topic_groups), bind_host, default_value, float_default
    )
    tabs = [
        _ServerTab(
            title=f"{server.host}:{server.port}",
            handler=cast(MultiUnitDataHandler, server.data_hdl),
            rows=build_rows(list(topics)),
        )
        for (topics, _), server in zip(topic_groups, stub.servers, strict=True)
    ]

    for server in stub.servers:
        server.start()
        logger.info("Stub serving on %s:%d", server.host, server.port)
    try:
        StubTui(tabs).run()
    finally:
        for server in stub.servers:
            server.stop()
