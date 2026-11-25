from unittest.mock import MagicMock

import pytest

from zero_modbus_bridge.writer import ModbusWriteError, ModbusWriter


def test_write_writes_registers_in_order_to_unit():
    modbus = MagicMock(is_open=True)
    modbus.write_single_register.return_value = True

    ModbusWriter(modbus).write(35, [(11, 1), (12, 4500), (10, 1)])

    assert modbus.unit_id == 35
    assert [c.args for c in modbus.write_single_register.call_args_list] == [
        (11, 1),
        (12, 4500),
        (10, 1),
    ]


def test_write_stops_at_first_failed_register():
    modbus = MagicMock(is_open=True)
    modbus.write_single_register.side_effect = [True, None, True]

    with pytest.raises(ModbusWriteError, match="register 12 of unit 35"):
        ModbusWriter(modbus).write(35, [(11, 1), (12, 4500), (10, 1)])

    assert modbus.write_single_register.call_count == 2


def test_write_opens_a_closed_connection():
    modbus = MagicMock(is_open=False)
    modbus.open.return_value = True
    modbus.write_single_register.return_value = True

    ModbusWriter(modbus).write(1, [(10, 1)])

    modbus.open.assert_called_once()


def test_write_raises_when_gateway_unreachable():
    modbus = MagicMock(is_open=False)
    modbus.open.return_value = False

    with pytest.raises(ModbusWriteError, match="unavailable"):
        ModbusWriter(modbus).write(1, [(10, 1)])

    modbus.write_single_register.assert_not_called()
