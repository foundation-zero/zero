import time
from typing import List

from pyModbusTCP.constants import EXP_NONE, EXP_SLAVE_DEVICE_FAILURE
from pyModbusTCP.server import DataHandler, ModbusServer

from zero_termodinamica.addresses import ModbusUnit
from zero_termodinamica.settings import ModbusSettings


class MultiUnitDataHandler(DataHandler):
    def __init__(self, data: List[ModbusUnit], default_value: int):
        super().__init__()
        self.data = {}
        for unit in data:
            self.data[unit.unit_id] = {
                addr.register: default_value
                for topic in unit.topics
                for addr in topic.fields
            }

    def read_h_regs(self, address, count, srv_info):
        unit_id = srv_info.recv_frame.mbap.unit_id
        if unit_id not in self.data:
            print(f"Unit ID {unit_id} not found")
            return DataHandler.Return(exp_code=EXP_SLAVE_DEVICE_FAILURE)

        unit_registers = self.data[unit_id]
        try:
            value = unit_registers[address]
            return DataHandler.Return(EXP_NONE, data=[value])
        except ValueError:
            print(f"Invalid address: {address}")
            return DataHandler.Return(exp_code=EXP_SLAVE_DEVICE_FAILURE)
        except IndexError:
            print(f"Address out of range: {address}")
            return DataHandler.Return(exp_code=EXP_SLAVE_DEVICE_FAILURE)


class Stub:
    def __init__(
        self,
        modbus: ModbusServer,
    ):
        self._modbus = modbus

    @staticmethod
    def from_settings(
        modbus_settings: ModbusSettings,
        modbus_data: List[ModbusUnit],
        default_value: int,
    ) -> "Stub":
        data_handler = MultiUnitDataHandler(modbus_data, default_value)
        return Stub(modbus_settings.modbus_server(data_handler))

    def run(self):
        self._modbus.start()
        while True:
            time.sleep(1)
