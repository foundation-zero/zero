from typing import Annotated

import pytest
from pydantic import BaseModel, Field
from textual.widgets import DataTable, Input, TabbedContent, Tabs

from zero_modbus_bridge.io import (
    AnnotationModbusTopic,
    ConverterModbusTopic,
    ModbusField,
    ModbusTopic,
)
from zero_modbus_bridge.stub import MultiUnitDataHandler
from zero_modbus_bridge.tui import (
    EditScreen,
    StubTui,
    _ServerTab,
    build_rows,
    format_value,
    human_value,
    write_value,
)


class SensorModel(BaseModel):
    temperature: Annotated[
        float | None,
        ModbusField(offset=0, data_type="float32"),
        Field(json_schema_extra={"x-unit": "degC"}),
    ]
    current: Annotated[
        int | None,
        ModbusField(offset=2, scale_factor=0.1),
        Field(json_schema_extra={"x-unit": "A"}),
    ]


def _sensor_topic(start_register: int = 100) -> AnnotationModbusTopic:
    return AnnotationModbusTopic(
        topic="test/sensor", model=SensorModel, start_register=start_register, unit_id=3
    )


def _handler() -> MultiUnitDataHandler:
    return MultiUnitDataHandler([_sensor_topic()], default_value=0)


def test_build_rows_annotation_names_and_units():
    rows = build_rows([_sensor_topic()])

    assert [row.name for row in rows] == ["temperature", "current"]
    assert [row.address for row in rows] == [100, 102]
    assert [row.data_type for row in rows] == ["float32", "uint16"]
    assert [row.scale_factor for row in rows] == [1.0, 0.1]
    assert [row.unit for row in rows] == ["degC", "A"]
    assert all(row.unit_id == 3 for row in rows)


def test_build_rows_converter_uses_register_as_name():
    class PlainModel(BaseModel):
        pass

    topic = ConverterModbusTopic(
        topic="hull/temp",
        model=PlainModel,
        fields=[
            ModbusField(register=9203, data_type="float32"),
            ModbusField(register=9205, data_type="float32"),
        ],
        converter=lambda values: PlainModel(),
    )

    rows = build_rows([topic])

    assert [row.name for row in rows] == ["9203", "9205"]
    assert [row.address for row in rows] == [9203, 9205]
    assert [row.unit for row in rows] == [None, None]


def test_human_value_scales_and_format_value():
    handler = _handler()
    rows = build_rows([_sensor_topic()])
    temperature, current = rows

    handler.set_float(3, 100, 23.5)
    handler.set_register(3, 102, 230)

    assert human_value(handler, temperature) == 23.5
    assert human_value(handler, current) == 23.0
    assert format_value(human_value(handler, temperature), "float32") == "23.5"
    assert format_value(human_value(handler, current), "uint16") == "23"


def test_write_value_float_round_trip():
    handler = _handler()
    rows = build_rows([_sensor_topic()])

    write_value(handler, rows[0], "23.5")

    assert handler.read_float(3, 100) == 23.5


def test_write_value_uint16_scales_and_clamps():
    handler = _handler()
    rows = build_rows([_sensor_topic()])

    write_value(handler, rows[1], "23")
    assert handler.read_register(3, 102) == 230

    write_value(handler, rows[1], "999999")
    assert handler.read_register(3, 102) == 65535


def test_write_value_invalid_text_raises():
    handler = _handler()
    rows = build_rows([_sensor_topic()])

    with pytest.raises(ValueError):
        write_value(handler, rows[0], "not-a-number")


async def test_tui_edit_flow_writes_to_handler():
    topic = _sensor_topic()
    handler = MultiUnitDataHandler([topic], float_default=20.0)
    tab = _ServerTab(title="stub", handler=handler, rows=build_rows([topic]))
    app = StubTui([tab])

    async with app.run_test() as pilot:
        table = app.query_one(DataTable)
        table.focus()
        await pilot.press("enter")

        edit = app.screen
        assert isinstance(edit, EditScreen)
        edit.query_one(Input).value = ""
        await pilot.press(*"23.5")
        await pilot.press("enter")

        assert handler.read_float(3, 100) == 23.5


async def test_tui_scrolls_cursor_past_the_fold():
    topics: list[ModbusTopic] = [
        _sensor_topic(start_register=1000 + index * 10) for index in range(46)
    ]
    handler = MultiUnitDataHandler(topics)
    tab = _ServerTab(title="stub", handler=handler, rows=build_rows(topics))
    app = StubTui([tab])

    async with app.run_test(size=(90, 24)) as pilot:
        table = app.query_one(DataTable)
        table.focus()
        for _ in range(30):
            await pilot.press("down")
            if table.scroll_y > 0:
                break

        assert table.scroll_y > 0


async def test_tui_tab_cycles_focus_and_arrows_switch_servers():
    def server_tab(title: str, start_register: int) -> _ServerTab:
        topic = _sensor_topic(start_register)
        return _ServerTab(
            title=title, handler=MultiUnitDataHandler([topic]), rows=build_rows([topic])
        )

    app = StubTui([server_tab("a", 100), server_tab("b", 200)])

    async with app.run_test(size=(90, 24)) as pilot:
        content = app.query_one(TabbedContent)
        regions = (app.query_one("#filter", Input).region, content.region)

        await pilot.press("tab")
        assert isinstance(app.focused, Tabs)

        await pilot.press("right")
        assert content.active == "server-1"
        await pilot.press("left")
        assert content.active == "server-0"

        await pilot.press("tab")
        assert isinstance(app.focused, DataTable)
        assert (app.query_one("#filter", Input).region, content.region) == regions
