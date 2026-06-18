import time

from pyModbusTCP.server import ModbusServer

from zero_termodinamica.addresses import ADDRESSES
from zero_termodinamica.settings import ModbusSettings


class Stub:
    def __init__(
        self,
        modbus: ModbusServer,
        default_value: int = 10,
    ):
        self._modbus = modbus
        for address in ADDRESSES:
            self._modbus.data_bank.set_holding_registers(
                address.register, [default_value]
            )

    @staticmethod
    def from_settings(
        modbus_settings: ModbusSettings,
        default_value: int,
    ) -> "Stub":
        return Stub(
            modbus_settings.modbus_server(),
            default_value,
        )

    def run(self):
        self._modbus.start()
        while True:
            time.sleep(1)
