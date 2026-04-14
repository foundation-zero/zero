from dataclasses import dataclass
from enum import Enum
import struct
from typing import assert_never, cast
from pyModbusTCP.client import ModbusClient

from zero_prop_test.settings import ModbusSettings


class RegisterType(Enum):
    COIL = 1
    DISCRETE_INPUT = 2
    INPUT = 3
    HOLDING = 4


@dataclass
class Register[T]:
    address: int
    scaling: int | None
    datatype: type[T]
    type: RegisterType

    def parse_registers(self, data: list[int]) -> T:
        if self.datatype is float:
            # TODO: verify word order in the field
            b = struct.pack("<HH", *data)  # 2 words
            val = struct.unpack("<f", b)[0]  # Read as float
            return val * self.scaling if self.scaling else val
        elif self.datatype is int:
            return cast(T, data[0] * self.scaling if self.scaling else data[0])
        else:
            raise ValueError(
                f"Unsupported datatype {self.datatype}, only int and float are supported for register parsing"
            )

    @property
    def length(self) -> int:
        if self.datatype is bool:
            return 1
        elif self.datatype is int:
            return 1
        elif self.datatype is float:
            return 2
        else:
            raise ValueError(f"Unsupported datatype {self.datatype}")


class Client:
    def __init__(self, client: ModbusClient):
        self._client = client

    @staticmethod
    def from_settings(settings: ModbusSettings) -> "Client":
        return Client(
            ModbusClient(
                host=settings.modbus_host,
                port=settings.modbus_port,
                auto_open=True,
            )
        )

    def _verify_response[T: int | bool](self, response: list[T] | None) -> list[T]:
        if response is None:
            raise ValueError("No response received from Modbus server")
        if isinstance(response, list) and len(response) == 0:
            raise ValueError("Empty response received from Modbus server")
        return response

    def query[T](self, register: Register[T]) -> T:
        if register.type == RegisterType.COIL:
            data = self._client.read_coils(register.address, register.length)
            data = self._verify_response(data)
            return cast(T, data[0])
        elif register.type == RegisterType.DISCRETE_INPUT:
            data = self._client.read_discrete_inputs(register.address, register.length)
            data = self._verify_response(data)
            return cast(T, data[0])
        elif register.type == RegisterType.INPUT:
            data = self._client.read_input_registers(register.address, register.length)
            data = self._verify_response(data)
            return register.parse_registers(data)
        elif register.type == RegisterType.HOLDING:
            data = self._client.read_holding_registers(
                register.address, register.length
            )
            data = self._verify_response(data)
            return register.parse_registers(data)
        else:
            assert_never(register.type)


@dataclass
class Address:
    name: str
    yard_tag: str
    register: Register


ADDRESSES = [
    Address(
        name="thrusters-temperature-aft-return",
        yard_tag="50001038-01",
        register=Register(
            address=9203, scaling=None, datatype=float, type=RegisterType.HOLDING
        ),
    ),
    Address(
        name="thrusters-temperature-fwd-return",
        yard_tag="50001038-02",
        register=Register(
            address=9205, scaling=None, datatype=float, type=RegisterType.HOLDING
        ),
    ),
]
