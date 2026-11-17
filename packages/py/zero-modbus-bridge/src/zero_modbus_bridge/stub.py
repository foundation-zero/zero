import logging
import time
from collections.abc import Sequence

from pyModbusTCP.constants import EXP_NONE, EXP_SLAVE_DEVICE_FAILURE
from pyModbusTCP.server import DataHandler, ModbusServer

from zero_modbus_bridge.bit_ops import float_to_lsw_registers, lsw_registers_to_float
from zero_modbus_bridge.io import ModbusField, ModbusTopic, extract_modbus_fields
from zero_modbus_bridge.settings import ModbusSettings


def _resolve_register(field: ModbusField, start: int) -> int:
    if field.offset is not None:
        return start + field.offset
    if field.register is not None:
        return field.register
    raise ValueError("ModbusField has neither register nor offset")


def _iter_fields(topics: list[ModbusTopic]) -> list[tuple[int, ModbusField]]:
    """Flatten all fields from every topic into ``(register, ModbusField)`` pairs."""
    topic_fields = [
        (
            topic.start_register,
            topic.fields or list(extract_modbus_fields(topic.model).values()),
        )
        for topic in topics
    ]

    return [
        (_resolve_register(field, start_register), field)
        for start_register, fields in topic_fields
        for field in fields
    ]


class MultiUnitDataHandler(DataHandler):
    def __init__(
        self,
        data: list[ModbusTopic],
        default_value: int = 0,
        float_default: float | None = None,
    ):
        super().__init__()
        self.data: dict[int, dict[int, int]] = {}
        self._float_registers: dict[int, dict[int, list[int]]] = {}
        self._coils: dict[int, dict[int, bool]] = {}
        self._coil_default: bool = bool(default_value)
        for topic in data:
            self._init_topic(topic, default_value, float_default)

    def _init_topic(
        self,
        topic: ModbusTopic,
        default_value: int,
        float_default: float | None,
    ) -> None:
        """Initialize register maps for one topic."""
        uid = topic.unit_id
        if uid not in self.data:
            self.data[uid] = {}
            self._float_registers[uid] = {}
            self._coils[uid] = {}
        for reg, field in _iter_fields([topic]):
            if field.modbus_type == "coil":
                self._coils[uid][reg] = self._coil_default
            elif field.data_type == "float32" and field.count == 2:
                regs = (
                    float_to_lsw_registers(float_default)
                    if float_default is not None
                    else [default_value, default_value]
                )
                self._float_registers[uid][reg] = regs
                self.data[uid][reg] = regs[0]
                self.data[uid][reg + 1] = regs[1]
            else:
                self.data[uid][reg] = default_value

    def read_register(self, unit_id: int, address: int) -> int:
        """Return the raw uint16 value stored at ``address`` for ``unit_id``."""
        if unit_id not in self.data or address not in self.data[unit_id]:
            raise ValueError(f"Register {address} not defined for unit {unit_id}")
        return self.data[unit_id][address]

    def read_float(self, unit_id: int, address: int) -> float:
        """Return the float32 value stored at ``address`` for ``unit_id``."""
        if (
            unit_id not in self._float_registers
            or address not in self._float_registers[unit_id]
        ):
            raise ValueError(f"Float register {address} not defined for unit {unit_id}")
        return lsw_registers_to_float(self._float_registers[unit_id][address])

    def set_register(self, unit_id: int, address: int, value: int) -> None:
        """Store a raw uint16 value at ``address`` for ``unit_id``."""
        if unit_id not in self.data or address not in self.data[unit_id]:
            raise ValueError(f"Register {address} not defined for unit {unit_id}")
        self.data[unit_id][address] = value

    def set_float(self, unit_id: int, address: int, value: float) -> None:
        """Store a float32 value at ``address`` for ``unit_id``.

        ``address`` is the first of the two registers backing the float.
        """
        if (
            unit_id not in self._float_registers
            or address not in self._float_registers[unit_id]
        ):
            raise ValueError(f"Float register {address} not defined for unit {unit_id}")
        low, high = float_to_lsw_registers(value)
        self._float_registers[unit_id][address] = [low, high]
        self.data[unit_id][address] = low
        self.data[unit_id][address + 1] = high

    def read_h_regs(self, address: int, count: int, srv_info):
        unit_id = srv_info.recv_frame.mbap.unit_id
        if unit_id not in self.data:
            logging.warning("Unit ID %s not found", unit_id)
            return DataHandler.Return(exp_code=EXP_SLAVE_DEVICE_FAILURE)
        if count == 2 and unit_id in self._float_registers:
            float_regs = self._float_registers[unit_id]
            if address in float_regs:
                return DataHandler.Return(EXP_NONE, data=float_regs[address])
        unit_registers = self.data[unit_id]
        if address not in unit_registers:
            logging.warning("Address %s not found for unit %s", address, unit_id)
            return DataHandler.Return(exp_code=EXP_SLAVE_DEVICE_FAILURE)

        registers = range(address, address + count)
        missing_register = next(
            (register for register in registers if register not in unit_registers),
            None,
        )
        if missing_register is not None:
            logging.warning(
                "Address %s not found for unit %s", missing_register, unit_id
            )
            return DataHandler.Return(exp_code=EXP_SLAVE_DEVICE_FAILURE)

        values = [unit_registers[register] for register in registers]
        return DataHandler.Return(EXP_NONE, data=values)

    def read_coils(self, address: int, count: int, srv_info):
        unit_id = srv_info.recv_frame.mbap.unit_id
        if unit_id not in self._coils:
            logging.warning("Unit ID %s not found for coils", unit_id)
            return DataHandler.Return(exp_code=EXP_SLAVE_DEVICE_FAILURE)
        coil_map = self._coils[unit_id]
        if address not in coil_map:
            logging.warning("Coil address %s not found for unit %s", address, unit_id)
            return DataHandler.Return(exp_code=EXP_SLAVE_DEVICE_FAILURE)

        registers = range(address, address + count)
        missing_register = next(
            (register for register in registers if register not in coil_map),
            None,
        )
        if missing_register is not None:
            logging.warning(
                "Coil address %s not found for unit %s", missing_register, unit_id
            )
            return DataHandler.Return(exp_code=EXP_SLAVE_DEVICE_FAILURE)

        values = [int(coil_map[register]) for register in registers]
        return DataHandler.Return(EXP_NONE, data=values)


class Stub:
    def __init__(self, modbus_servers: list[ModbusServer]):
        self.servers = modbus_servers

    @staticmethod
    def from_settings(
        modbus_settings: ModbusSettings,
        modbus_data: list[ModbusTopic],
        default_value: int = 0,
        float_default: float | None = None,
    ) -> "Stub":
        return Stub.from_topic_groups(
            [(modbus_data, modbus_settings.modbus_port)],
            bind_host=modbus_settings.modbus_host,
            default_value=default_value,
            float_default=float_default,
        )

    @staticmethod
    def from_topic_groups(
        topic_groups: Sequence[tuple[Sequence[ModbusTopic], int]],
        bind_host: str = "0.0.0.0",
        default_value: int = 0,
        float_default: float | None = None,
    ) -> "Stub":
        """One server per ``(topics, port)`` group.

        Serves setups with several gateways that each expose their own topic
        group; every group gets a private register space, mirroring physically
        separate devices.
        """
        servers = [
            ModbusServer(
                bind_host,
                port,
                no_block=True,
                data_hdl=MultiUnitDataHandler(
                    list(topics), default_value, float_default
                ),
            )
            for topics, port in topic_groups
        ]
        return Stub(servers)

    def run(self) -> None:
        for server in self.servers:
            server.start()
        while True:
            time.sleep(1)
