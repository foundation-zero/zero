import logging
from asyncio import (
    Task,
    create_task,
    get_running_loop,
)

from pyModbusTCP.server import DataBank, ModbusServer

from domestic_control.services.ventilation.constants import (
    CO2_SETPOINT_START_ADDRESS,
)


class VentilationDataBank(DataBank):
    def on_holding_registers_change(
        self, address, from_value, to_value, srv_info
    ) -> None:
        logging.debug(f"Stub: adress: {address}, from: {from_value}, to: {to_value}")
        if address >= CO2_SETPOINT_START_ADDRESS.start and address < (
            CO2_SETPOINT_START_ADDRESS.start + 100
        ):
            self.set_holding_registers(address - 100, [to_value])
        return super().on_holding_registers_change(
            address, from_value, to_value, srv_info
        )


class VentilationStub:
    """Stub for a Ventilation Modbus TCP control system"""

    def __init__(self, host, port):
        self._server = ModbusServer(
            host=host, port=port, data_bank=VentilationDataBank()
        )
        self._host = host
        self._port = port

    def _start_server(self) -> Task[None]:
        async def _start():
            await get_running_loop().run_in_executor(None, self._server.start)

        server_run = create_task(_start())
        server_run.add_done_callback(lambda _: self._server.stop())
        return server_run

    async def run(self):
        logging.info(f"Starting Ventilation stub on {self._host}:{self._port}")
        await self._start_server()
