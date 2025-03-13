from asyncio import TaskGroup, sleep
import re
import time
from typing import Literal, cast
from aiomqtt import Client as MqttClient, Message

from zero_domestic_control.services.av import AFT_PDU, FWD_PDU, PortState, Telemetry

MQTT_CMD_REGEX = re.compile(r"de/gudesystems/epc/([^/]+)/cmdres/port/(\d+)")
AV_STUB_TELEMETRY_INTERVAL = 0.5


class AvPduStub:
    """Stub for an AV PDU (Power Distribution Unit)"""

    def __init__(self, mqtt_client: MqttClient, pdu: str):
        self._mqtt_client = mqtt_client
        self._ports = {port: False for port in range(1, 11)}
        self._pdu = pdu

    async def step(self):
        async with TaskGroup() as tg:
            tg.create_task(self.send_telemetry())
            tg.create_task(sleep(AV_STUB_TELEMETRY_INTERVAL))

    async def run_telemetry(self):
        while True:
            await self.step()

    def read_port(self, port: int):
        return self._ports[port]

    def set_port(self, port: int, state: bool):
        self._ports[port] = state

    def _create_telemetry(self, ports: dict[int, bool]) -> Telemetry:
        return Telemetry(
            timestamp=int(time.time()),
            port_states=[
                PortState(port=port, state=cast(Literal[0, 1], int(state)))
                for port, state in ports.items()
            ],
        )

    def match_message(self, message: Message):
        if match := MQTT_CMD_REGEX.match(message.topic.value):
            pdu, port = match.groups()
            if pdu == self._pdu:
                return (self, port)
        return None

    async def process_messages(self, port: str, message: Message):
        if isinstance(message.payload, str | bytes):
            self._ports[int(port)] = bool(int(message.payload))

    async def send_telemetry(self):
        telemetry = self._create_telemetry(self._ports)
        print(f"Sent telemetry for {self._pdu}")
        await self._mqtt_client.publish(
            f"de/gudesystems/epc/{self._pdu}/device/telemetry",
            telemetry.model_dump_json(),
            qos=0,
        )


class AvStub:
    def __init__(self, mqtt_client: MqttClient):
        self._mqtt_client = mqtt_client
        self._pdus = [AvPduStub(mqtt_client, FWD_PDU), AvPduStub(mqtt_client, AFT_PDU)]

    async def handle_messages(self):
        async for message in self._mqtt_client.messages:
            match = next(
                (match for pdu in self._pdus if (match := pdu.match_message(message))),
                None,
            )
            if match:
                pdu, port = match
                await pdu.process_messages(port, message)
            else:
                raise ValueError(f"Unknown message {message.topic.value}")

    def _lookup_pdu(self, pdu: str):
        return next(stub for stub in self._pdus if stub._pdu == pdu)

    def read_port(self, pdu: str, port: int) -> bool:
        return self._lookup_pdu(pdu).read_port(port)

    def set_port(self, pdu: str, port: int, state: bool):
        self._lookup_pdu(pdu).set_port(port, state)

    async def run(self):
        await self._mqtt_client.subscribe("de/gudesystems/epc/+/cmdres/port/+", qos=1)

        async with TaskGroup() as tg:
            for pdu in self._pdus:
                tg.create_task(pdu.run_telemetry())
            tg.create_task(self.handle_messages())
