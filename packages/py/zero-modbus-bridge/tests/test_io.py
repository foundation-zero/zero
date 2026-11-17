from typing import Annotated

import pytest
from pydantic import BaseModel

from zero_modbus_bridge.io import (
    AnnotationModbusTopic,
    ConverterModbusTopic,
    ModbusField,
    apply_modbus_field,
    extract_modbus_fields,
)


def test_modbus_field_register_only():
    f = ModbusField(register=3000)
    assert f.register == 3000
    assert f.offset is None
    assert f.count == 1
    assert f.data_type == "uint16"
    assert f.modbus_type == "holding"
    assert f.scale_factor == 1.0
    assert f.validator is None


def test_modbus_field_offset_only():
    f = ModbusField(offset=0, data_type="float32")
    assert f.offset == 0
    assert f.register is None
    assert f.count == 2
    assert f.data_type == "float32"


def test_modbus_field_both_register_and_offset_raises():
    with pytest.raises(ValueError, match="Provide either"):
        ModbusField(register=3000, offset=10)


def test_modbus_field_neither_register_nor_offset():
    f = ModbusField()
    assert f.register is None
    assert f.offset is None


def test_apply_modbus_field_validator_rejects():
    field = ModbusField(register=10, validator=lambda raw: raw != 0xFFFF)
    assert apply_modbus_field(0xFFFF, field) is None
    assert apply_modbus_field(100, field) == 100.0


class _TestModel(BaseModel):
    current_a: Annotated[float | None, ModbusField(offset=0, data_type="float32")]
    power: Annotated[int | None, ModbusField(register=100, scale_factor=0.01)]
    flag: Annotated[
        bool | None, ModbusField(register=200, modbus_type="coil", data_type="bool")
    ]


def test_extract_modbus_fields():
    fields = extract_modbus_fields(_TestModel)
    assert set(fields) == {"current_a", "power", "flag"}
    assert fields["current_a"].offset == 0
    assert fields["current_a"].count == 2
    assert fields["current_a"].data_type == "float32"
    assert fields["power"].register == 100
    assert fields["power"].scale_factor == 0.01
    assert fields["flag"].register == 200
    assert fields["flag"].modbus_type == "coil"
    assert fields["flag"].data_type == "bool"


class _PlainModel(BaseModel):
    x: int


def test_extract_modbus_fields_no_annotations():
    fields = extract_modbus_fields(_PlainModel)
    assert fields == {}


def test_modbus_topic_annotation_driven():
    topic = AnnotationModbusTopic(
        topic="test/foo",
        model=_TestModel,
        start_register=3000,
        unit_id=2,
        extra_fields={"room": "Lounge"},
    )
    assert topic.topic == "test/foo"
    assert topic.model is _TestModel
    assert topic.start_register == 3000
    assert topic.unit_id == 2
    assert topic.extra_fields == {"room": "Lounge"}
    assert topic.fields is not None
    assert len(topic.fields) == 3
    assert topic.converter is not None


def test_modbus_topic_converter_driven():
    class ConverterModel(BaseModel):
        x: int

    def fake_converter(values):
        return ConverterModel(x=1)

    topic = ConverterModbusTopic(
        topic="test/bar",
        model=_PlainModel,
        fields=[ModbusField(register=42)],
        converter=fake_converter,
    )
    assert topic.converter is fake_converter
    assert topic.fields is not None
    assert topic.fields[0].register == 42
    assert topic.converter is not None


def test_modbus_topic_extra_fields_not_shared():
    topic_a = AnnotationModbusTopic(topic="test/a", model=_PlainModel)
    topic_b = AnnotationModbusTopic(topic="test/b", model=_PlainModel)

    topic_a.extra_fields["key"] = "value"
    assert topic_b.extra_fields == {}
