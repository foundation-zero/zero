from unittest.mock import MagicMock
from pyModbusTCP.client import ModbusClient
from zero_prop_test.modbus import Register, RegisterType, Client


def test_register_parse():
    register = Register[float](
        address=0, scaling=None, datatype=float, type=RegisterType.HOLDING
    )
    assert register.parse_registers([0xD4E6, 0x419D]) == 19.728954315185547


def test_client():
    mock = MagicMock(spec=ModbusClient)
    mock.read_holding_registers.return_value = [0xD4E6, 0x419D]
    client = Client(mock)
    result = client.query(
        Register[float](
            address=0, scaling=None, datatype=float, type=RegisterType.HOLDING
        )
    )
    assert result == 19.728954315185547
    mock.read_holding_registers.assert_called_once_with(0, 2)
