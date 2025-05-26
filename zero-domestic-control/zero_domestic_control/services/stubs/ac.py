from asyncio import (
    Task,
    create_task,
    get_running_loop,
)
from pyModbusTCP.server import DataBank, ModbusServer

from zero_domestic_control.services.ac.constants import (
    HUMIDITY_SETPOINT_START_ADDRESS,
    TEMPERATURE_SETPOINT_START_ADDRESS,
)
import logging


class TermodinamicaDataBank(DataBank):
    def on_holding_registers_change(
        self, address, from_value, to_value, srv_info
    ) -> None:
        if address >= TEMPERATURE_SETPOINT_START_ADDRESS.start and address < (
            TEMPERATURE_SETPOINT_START_ADDRESS.start + 100
        ):
            self.set_holding_registers(address - 100, [to_value])
        elif address >= HUMIDITY_SETPOINT_START_ADDRESS.start and address < (
            HUMIDITY_SETPOINT_START_ADDRESS.start + 100
        ):
            self.set_holding_registers(address - 100, [to_value])
        return super().on_holding_registers_change(
            address, from_value, to_value, srv_info
        )


class TermodinamicaStub:
    """Stub for a Termodinamica AC Modbus TCP control system"""

    def __init__(self, host, port):
        self._server = ModbusServer(
            host=host, port=port, data_bank=TermodinamicaDataBank()
        )
        logging.info(f"Starting Termodinamica stub on {host}:{port}")

    def _start_server(self) -> Task[None]:
        async def _start():
            await get_running_loop().run_in_executor(None, self._server.start)

        server_run = create_task(_start())
        server_run.add_done_callback(lambda _: self._server.stop())
        return server_run

    async def run(self):
        await self._start_server()
