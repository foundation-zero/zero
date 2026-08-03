from types import SimpleNamespace
from typing import Annotated

from pydantic import BaseModel
from pyModbusTCP.constants import EXP_NONE, EXP_SLAVE_DEVICE_FAILURE

from zero_modbus_bridge.io import AnnotationModbusTopic, ModbusField
from zero_modbus_bridge.stub import MultiUnitDataHandler


def _srv_info(unit_id: int):
    return SimpleNamespace(recv_frame=SimpleNamespace(mbap=SimpleNamespace(unit_id=unit_id)))


class TwoRegistersModel(BaseModel):
    first: Annotated[int | None, ModbusField(offset=0)]
    second: Annotated[int | None, ModbusField(offset=1)]


class TwoCoilsModel(BaseModel):
    first: Annotated[
        bool | None, ModbusField(offset=0, modbus_type="coil", data_type="bool")
    ]
    second: Annotated[
        bool | None, ModbusField(offset=1, modbus_type="coil", data_type="bool")
    ]


def test_stub_read_h_regs_returns_multiple_registers():
    topic = AnnotationModbusTopic(topic="test/regs", model=TwoRegistersModel, start_register=10)
    handler = MultiUnitDataHandler([topic], default_value=7)

    ret = handler.read_h_regs(10, 2, _srv_info(1))
    assert ret.exp_code == EXP_NONE
    assert ret.data == [7, 7]


def test_stub_read_h_regs_missing_address_returns_error():
    topic = AnnotationModbusTopic(topic="test/regs", model=TwoRegistersModel, start_register=10)
    handler = MultiUnitDataHandler([topic], default_value=7)

    ret = handler.read_h_regs(999, 1, _srv_info(1))
    assert ret.exp_code == EXP_SLAVE_DEVICE_FAILURE


def test_stub_read_coils_missing_address_returns_error():
    topic = AnnotationModbusTopic(topic="test/coils", model=TwoCoilsModel, start_register=20)
    handler = MultiUnitDataHandler([topic], default_value=1)

    ret = handler.read_coils(999, 1, _srv_info(1))
    assert ret.exp_code == EXP_SLAVE_DEVICE_FAILURE


def test_stub_read_coils_returns_multiple_values():
    topic = AnnotationModbusTopic(topic="test/coils", model=TwoCoilsModel, start_register=20)
    handler = MultiUnitDataHandler([topic], default_value=1)

    ret = handler.read_coils(20, 2, _srv_info(1))
    assert ret.exp_code == EXP_NONE
    assert ret.data == [1, 1]
