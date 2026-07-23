from typing import Annotated

from pydantic import BaseModel

from zero_modbus_bridge.io import ModbusField


class FloatModel(BaseModel):
    value: Annotated[float | None, ModbusField(offset=0, count=2, data_type="float32")]
    room: str | None = None


class UintModel(BaseModel):
    val: Annotated[int | None, ModbusField(register=100, invalid_value=0xFFFF)]
    flag: Annotated[
        bool | None, ModbusField(register=200, modbus_type="coil", data_type="bool")
    ]


class ScaledModel(BaseModel):
    scaled: Annotated[float | None, ModbusField(register=10, scale_factor=0.04)]
