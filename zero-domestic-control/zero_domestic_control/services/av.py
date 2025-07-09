from contextlib import asynccontextmanager
import re
from aiomqtt import Client as MqttClient, Message
from pydantic import AliasChoices, BaseModel, Field
from typing import Annotated, AsyncIterable, Coroutine, List, Literal

from zero_domestic_control.config import Settings
from zero_domestic_control.messages import Amplifier
from zero_domestic_control.mqtt import DataCollection
from zero_domestic_control.util import invert_dict

FWD_PDU = "00:00:00:00:00:00"
AFT_PDU = "00:00:00:00:00:01"

FWD_PORTS = {
    "office/amplifier": 1,  # office
    "lounge/amplifier": 2,  # lounge
}

AFT_PORTS = {
    "owners-cockpit/amplifier": 1,  # owners cockpit
    "owners-deckhouse/amplifier": 2,  # owners private salon
    "owners-cabin/amplifier": 3,  # owners cabin
    "main-cockpit/amplifier": 4,  # main cockpit
    "italian-cabin/amplifier": 5,  # guest PS FWD
    "galley/amplifier": 6,  # galley
    "french-cabin/amplifier": 7,  # guest PS AFT
    "dutch-cabin/amplifier": 8,  # guest SB AFT
    "polynesian-cabin/amplifier": 9,  # guest PS MID (also incorrectly named SB MID in overview drawing)
    "main-deckhouse/amplifier": 10,  # main salon
}


FWD_PORTS_INV = invert_dict(FWD_PORTS)
AFT_PORTS_INV = invert_dict(AFT_PORTS)


def lookup_room_id(pdu: str, switch: int) -> str | None:
    if pdu == FWD_PDU:
        return FWD_PORTS_INV.get(switch)
    elif pdu == AFT_PDU:
        return AFT_PORTS_INV.get(switch)
    else:
        raise ValueError(f"Unknown PDU {pdu}")


def lookup_pdu_switch(room_id: str) -> tuple[str, int]:
    if room_id in FWD_PORTS:
        return (FWD_PDU, FWD_PORTS[room_id])
    elif room_id in AFT_PORTS:
        return (AFT_PDU, AFT_PORTS[room_id])
    else:
        raise ValueError(f"Unknown room {room_id}")


class PortState(BaseModel):
    """Port state of a Gude PDU"""

    port: int
    state: Literal[0, 1]


class Telemetry(BaseModel):
    """Telemetry from a Gude PDU"""

    timestamp: Annotated[
        int,
        Field(
            validation_alias=AliasChoices("ts", "timestamp"),
            serialization_alias="ts",
        ),
    ]
    port_states: Annotated[
        List[PortState],
        Field(
            validation_alias=AliasChoices("portstates", "port_states"),
            serialization_alias="portstates",
        ),
    ]


PDU_REGEX = re.compile(r"de/gudesystems/epc/([^/]+)/device/telemetry")


class Gude:
    """Domain representation of the Gude PDU MQTT interface"""

    def __init__(self, mqtt_client: MqttClient):
        self._mqtt_client = mqtt_client

    async def switch(self, pdu: str, port: int, state: bool):
        await self._mqtt_client.publish(
            f"de/gudesystems/epc/{pdu}/cmdres/port/{port}", str(int(state)), qos=1
        )

    def extract_telemetry(self, message: Message) -> tuple[str, Telemetry] | None:
        if isinstance(message.payload, bytes | str):
            match = PDU_REGEX.match(message.topic.value)
            if match:
                pdu = match.group(1)
                return pdu, Telemetry.model_validate_json(message.payload)
        return None

    async def listen_to_all_telemetry(self):
        await self._mqtt_client.subscribe(
            "de/gudesystems/epc/+/device/telemetry", qos=1
        )

    @property
    async def telemetries(self) -> AsyncIterable[tuple[str, Telemetry]]:
        async for message in self._mqtt_client.messages:
            if pdu_telemetry := self.extract_telemetry(message):
                yield pdu_telemetry


class Av:
    """AV switching control"""

    def __init__(self, gude: Gude, data: DataCollection):
        self._gude = gude
        self._data = data

    async def set_amplifier(self, room_id: str, on: bool):
        pdu, switch = lookup_pdu_switch(room_id)
        await self._gude.switch(pdu, switch, on)
        # Also send directly to MQTT, telemetry is only send every so often, so this will be faster
        await self._data.send_amplifier(
            Amplifier(
                id=room_id,
                is_on=on,
            )
        )

    def validate_room_ids(self, ids: list[str]):
        if invalid := set(ids) - (set(FWD_PORTS.keys()) | set(AFT_PORTS.keys())):
            raise ValueError(f"Invalid room IDs {invalid}")


class AvControl:
    """AV control which collects and forwards the PDU telemetry to MQTT"""

    def __init__(self, gude: Gude, data: DataCollection):
        self._gude = gude
        self._data = data

    async def handle_telemetry(self, pdu: str, telemetry: Telemetry):
        for port_state in telemetry.port_states:
            room_id = lookup_room_id(pdu, port_state.port)
            if room_id is not None:
                await self._data.send_amplifier(
                    Amplifier(
                        id=room_id,
                        is_on=bool(port_state.state),
                    )
                )

    async def run(self) -> Coroutine[None, None, None]:
        """Run the AvControl service.

        The returned awaitable finishes when the control is actually running.
        Then the coroutine contained within can be run in an event loop.
        """
        await self._gude.listen_to_all_telemetry()

        async def _run():
            async for pdu, telemetry in self._gude.telemetries:
                await self.handle_telemetry(pdu, telemetry)

        return _run()

    @asynccontextmanager
    @staticmethod
    async def init_from_settings(settings: Settings):
        async with MqttClient(settings.mqtt_host, settings.mqtt_port) as mqtt_client:
            yield AvControl(Gude(mqtt_client), DataCollection(mqtt_client))
