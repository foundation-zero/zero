"""Hull temperature sensor addresses and bridge configuration."""

from typing import Annotated

from faststream.mqtt import MQTTBroker
from pydantic import BaseModel, ConfigDict, Field
from zero_modbus_bridge.bit_ops import is_finite_float
from zero_modbus_bridge.io import AnnotationModbusTopic, ModbusField
from zero_modbus_bridge.publisher import MappingPublisher, MqttPublisher

TOPIC = "marpower/450000-amcs/Command"
PATH = "$.KEB1_ACTIVATE_HULL_MEASUREMENT_ONOFF"


class HullTemperaturesModel(BaseModel):
    """Flat sensor readings with Modbus metadata and serial-number aliases.

    Each field is one physical probe. Python name is ``s_<serial with _>``
    (valid identifier), wire name is the original ``94455001-26`` serial via
    ``alias``.
    """

    model_config = ConfigDict(populate_by_name=True)

    # LOOP 1 — 14 probes
    s_94455001_26: Annotated[
        float | None,
        Field(default=None, alias="94455001-26"),
        ModbusField(register=9203, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_27: Annotated[
        float | None,
        Field(default=None, alias="94455001-27"),
        ModbusField(register=9205, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_28: Annotated[
        float | None,
        Field(default=None, alias="94455001-28"),
        ModbusField(register=9207, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_29: Annotated[
        float | None,
        Field(default=None, alias="94455001-29"),
        ModbusField(register=9209, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_34: Annotated[
        float | None,
        Field(default=None, alias="94455001-34"),
        ModbusField(register=9211, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_35: Annotated[
        float | None,
        Field(default=None, alias="94455001-35"),
        ModbusField(register=9213, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_30: Annotated[
        float | None,
        Field(default=None, alias="94455001-30"),
        ModbusField(register=9215, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_31: Annotated[
        float | None,
        Field(default=None, alias="94455001-31"),
        ModbusField(register=9217, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_32: Annotated[
        float | None,
        Field(default=None, alias="94455001-32"),
        ModbusField(register=9219, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_33: Annotated[
        float | None,
        Field(default=None, alias="94455001-33"),
        ModbusField(register=9221, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_24: Annotated[
        float | None,
        Field(default=None, alias="94455001-24"),
        ModbusField(register=9223, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_25: Annotated[
        float | None,
        Field(default=None, alias="94455001-25"),
        ModbusField(register=9225, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_36: Annotated[
        float | None,
        Field(default=None, alias="94455001-36"),
        ModbusField(register=9227, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_37: Annotated[
        float | None,
        Field(default=None, alias="94455001-37"),
        ModbusField(register=9229, data_type="float32", validator=is_finite_float),
    ] = None

    # LOOP 2 — 10 probes
    s_94455001_6: Annotated[
        float | None,
        Field(default=None, alias="94455001-6"),
        ModbusField(register=9235, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_7: Annotated[
        float | None,
        Field(default=None, alias="94455001-7"),
        ModbusField(register=9237, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_8: Annotated[
        float | None,
        Field(default=None, alias="94455001-8"),
        ModbusField(register=9239, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_9: Annotated[
        float | None,
        Field(default=None, alias="94455001-9"),
        ModbusField(register=9241, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_10: Annotated[
        float | None,
        Field(default=None, alias="94455001-10"),
        ModbusField(register=9243, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_11: Annotated[
        float | None,
        Field(default=None, alias="94455001-11"),
        ModbusField(register=9245, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_16: Annotated[
        float | None,
        Field(default=None, alias="94455001-16"),
        ModbusField(register=9247, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_17: Annotated[
        float | None,
        Field(default=None, alias="94455001-17"),
        ModbusField(register=9249, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_18: Annotated[
        float | None,
        Field(default=None, alias="94455001-18"),
        ModbusField(register=9251, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_19: Annotated[
        float | None,
        Field(default=None, alias="94455001-19"),
        ModbusField(register=9253, data_type="float32", validator=is_finite_float),
    ] = None

    # LOOP 3 — 13 probes
    s_94455001_20: Annotated[
        float | None,
        Field(default=None, alias="94455001-20"),
        ModbusField(register=9267, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_21: Annotated[
        float | None,
        Field(default=None, alias="94455001-21"),
        ModbusField(register=9269, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_22: Annotated[
        float | None,
        Field(default=None, alias="94455001-22"),
        ModbusField(register=9271, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_23: Annotated[
        float | None,
        Field(default=None, alias="94455001-23"),
        ModbusField(register=9273, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_12: Annotated[
        float | None,
        Field(default=None, alias="94455001-12"),
        ModbusField(register=9275, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_13: Annotated[
        float | None,
        Field(default=None, alias="94455001-13"),
        ModbusField(register=9277, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_14: Annotated[
        float | None,
        Field(default=None, alias="94455001-14"),
        ModbusField(register=9279, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_15: Annotated[
        float | None,
        Field(default=None, alias="94455001-15"),
        ModbusField(register=9281, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_2: Annotated[
        float | None,
        Field(default=None, alias="94455001-2"),
        ModbusField(register=9283, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_3: Annotated[
        float | None,
        Field(default=None, alias="94455001-3"),
        ModbusField(register=9285, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_1: Annotated[
        float | None,
        Field(default=None, alias="94455001-1"),
        ModbusField(register=9287, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_4: Annotated[
        float | None,
        Field(default=None, alias="94455001-4"),
        ModbusField(register=9289, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_5: Annotated[
        float | None,
        Field(default=None, alias="94455001-5"),
        ModbusField(register=9291, data_type="float32", validator=is_finite_float),
    ] = None

    # LOOP 4 — 9 probes
    s_94455001_38: Annotated[
        float | None,
        Field(default=None, alias="94455001-38"),
        ModbusField(register=9299, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_39: Annotated[
        float | None,
        Field(default=None, alias="94455001-39"),
        ModbusField(register=9301, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_40: Annotated[
        float | None,
        Field(default=None, alias="94455001-40"),
        ModbusField(register=9303, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_41: Annotated[
        float | None,
        Field(default=None, alias="94455001-41"),
        ModbusField(register=9305, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_42: Annotated[
        float | None,
        Field(default=None, alias="94455001-42"),
        ModbusField(register=9307, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_43: Annotated[
        float | None,
        Field(default=None, alias="94455001-43"),
        ModbusField(register=9309, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_44: Annotated[
        float | None,
        Field(default=None, alias="94455001-44"),
        ModbusField(register=9311, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_45: Annotated[
        float | None,
        Field(default=None, alias="94455001-45"),
        ModbusField(register=9313, data_type="float32", validator=is_finite_float),
    ] = None
    s_94455001_46: Annotated[
        float | None,
        Field(default=None, alias="94455001-46"),
        ModbusField(register=9315, data_type="float32", validator=is_finite_float),
    ] = None


class HullTemperature(BaseModel):
    """MQTT payload - single ``temperatures`` object.

    This is the publisher schema.
    """

    temperatures: HullTemperaturesModel = Field(default_factory=HullTemperaturesModel)


# Modbus reading is strictly the flat model; publishing wraps it to maintain MQTT compatibility
HULL_TEMPERATURE_TOPIC = AnnotationModbusTopic(
    topic="hull-temperature/temperatures",
    model=HullTemperaturesModel,
)


def _to_mqtt_payload(read: HullTemperaturesModel) -> HullTemperature:
    return HullTemperature(temperatures=read)


def create_publisher(broker: MQTTBroker) -> MappingPublisher:
    inner = MqttPublisher(
        broker,
        [HULL_TEMPERATURE_TOPIC],
        schemas={HULL_TEMPERATURE_TOPIC.topic: HullTemperature},
    )
    return MappingPublisher(inner, _to_mqtt_payload)
