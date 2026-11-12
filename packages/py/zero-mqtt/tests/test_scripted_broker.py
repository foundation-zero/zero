"""The broker and its check against a scripted MQTT 5 server on localhost."""

import asyncio
import gc
from functools import partial

import pytest
from faststream.mqtt import ReconnectConfig
from zero_health import Check

from zero_mqtt import MqttSettings, broker_check
from zero_mqtt import broker as broker_module

NOT_AUTHORIZED = 0x87
PINGREQ = 0xC0
PINGRESP = b"\xd0\x00"


class ScriptedServer:
    """Answers each CONNECT with the next CONNACK code, and pings if asked to."""

    def __init__(self, connack_codes: list[int], *, answer_pings: bool = True) -> None:
        self._codes = iter(connack_codes)
        self._answer_pings = answer_pings
        self._writers: list[asyncio.StreamWriter] = []
        self.connects = 0

    async def start(self) -> int:
        self._server = await asyncio.start_server(self._serve, "127.0.0.1", 0)
        return self._server.sockets[0].getsockname()[1]

    def drop(self) -> None:
        """Close every connection and stop listening, as a broker that died."""
        self._server.close()
        for writer in self._writers:
            writer.close()

    async def _serve(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        self._writers.append(writer)
        try:
            await _read_packet(reader)
            self.connects += 1
            writer.write(bytes([0x20, 3, 0, next(self._codes), 0]))
            while True:
                if await _read_packet(reader) == PINGREQ and self._answer_pings:
                    writer.write(PINGRESP)
        except asyncio.IncompleteReadError, ConnectionError:
            pass
        finally:
            writer.close()


async def _read_packet(reader: asyncio.StreamReader) -> int:
    """Read one packet and return its type byte."""
    packet_type = (await reader.readexactly(1))[0]
    length, shift = 0, 0
    while True:
        byte = (await reader.readexactly(1))[0]
        length |= (byte & 0x7F) << shift
        shift += 7
        if byte < 0x80:
            break
    await reader.readexactly(length)
    return packet_type & 0xF0


async def _wait_for_reason(check: Check, timeout: float = 5.0) -> str | None:
    async with asyncio.timeout(timeout):
        while (reason := await check()) is None:
            await asyncio.sleep(0.05)
    return reason


async def _connected_broker(server: ScriptedServer, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MQTT_HOST", "127.0.0.1")
    monkeypatch.setenv("MQTT_PORT", str(await server.start()))
    # Retry at once instead of after zmqtt's 1 s initial backoff.
    monkeypatch.setattr(
        broker_module, "ReconnectConfig", partial(ReconnectConfig, initial_delay=0.01)
    )
    return MqttSettings(_env_file=None).make_broker()  # type: ignore[call-arg]


async def test_check_follows_the_connection(monkeypatch: pytest.MonkeyPatch):
    server = ScriptedServer([NOT_AUTHORIZED, NOT_AUTHORIZED, 0])
    broker = await _connected_broker(server, monkeypatch)
    check = broker_check(broker)

    assert await check() == "ping failed"

    await broker.connect()
    try:
        assert server.connects == 3
        assert await check() is None

        server.drop()
        assert await _wait_for_reason(check) == "ping failed"
    finally:
        await broker.stop()


async def test_unanswered_ping_leaves_nothing_behind(monkeypatch: pytest.MonkeyPatch):
    server = ScriptedServer([0], answer_pings=False)
    broker = await _connected_broker(server, monkeypatch)
    errors: list[dict] = []
    asyncio.get_running_loop().set_exception_handler(lambda _, ctx: errors.append(ctx))
    await broker.connect()
    try:
        # As Health runs it: the check inside a longer check timeout.
        async with asyncio.timeout(1.0):
            assert await broker_check(broker, timeout=0.1)() == "ping failed"
        server.drop()
        await asyncio.sleep(0.2)  # let the client see the connection drop
    finally:
        await broker.stop()
    gc.collect()
    assert errors == []
