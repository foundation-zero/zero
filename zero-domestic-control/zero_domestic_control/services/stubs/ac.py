from asyncio import (
    Task,
    create_task,
    get_running_loop,
)
from pyModbusTCP.server import ModbusServer


class TermodinamicaStub:
    """Stub for a Termodinamica AC Modbus TCP control system"""

    def __init__(self, host, port):
        self._server = ModbusServer(host=host, port=port)

    def _start_server(self) -> Task[None]:
        async def _start():
            await get_running_loop().run_in_executor(None, self._server.start)

        server_run = create_task(_start())
        server_run.add_done_callback(lambda _: self._server.stop())
        return server_run

    async def run(self):
        await self._start_server()
