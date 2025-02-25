import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
import logging
from typing import Literal, assert_never
from homeassistant_api import Client as HassClient, WebsocketClient as HassWsClient
from pydantic import BaseModel

from zero_domestic_control.config import Settings
import re

from zero_domestic_control.messages import Blind, LightingGroup
from zero_domestic_control.mqtt import Mqtt
from zero_domestic_control.util import invert_dict

logger = logging.getLogger(__name__)

_id_replacer = re.compile(r"[-/]")


def id_to_hass_id(id: str) -> str:
    return _id_replacer.sub("_", id)


def hass_id_to_id(hass_id: str, type: Literal["light_group", "blinds"]) -> str | None:
    match type:
        case "light_group":
            return _LIGHT_GROUP_IDS_INV.get(hass_id.removeprefix("input_number."))
        case "blinds":
            return _BLIND_IDS_INV.get(hass_id.removeprefix("cover."))
        case default:
            assert_never(default)


_LIGHT_GROUP_IDS = {
    val: id_to_hass_id(val)
    for val in {
        "owners-cabin/ambient",
        "owners-cabin/mood",
        "dutch-cabin/ambient",
        "dutch-cabin/mood",
        "french-cabin/ambient",
        "french-cabin/mood",
        "italian-cabin/ambient",
        "italian-cabin/mood",
        "californian-lounge/ambient",
        "californian-lounge/mood",
        "polynesian-cabin/ambient",
        "polynesian-cabin/mood",
        "galley/ambient",
        "galley/mood",
        "crew-mess/ambient",
        "crew-mess/mood",
        "mission-room/ambient",
        "mission-room/mood",
        "laundry/ambient",
        "laundry/mood",
        "engineers-office/ambient",
        "engineers-office/mood",
        "captains-cabin/ambient",
        "captains-cabin/mood",
        "crew-sb-aft-cabin/ambient",
        "crew-sb-aft-cabin/mood",
        "crew-sb-mid-cabin/ambient",
        "crew-sb-mid-cabin/mood",
        "crew-sb-fwd-cabin/ambient",
        "crew-sb-fwd-cabin/mood",
        "crew-ps-mid-cabin/ambient",
        "crew-ps-mid-cabin/mood",
        "crew-ps-fwd-cabin/ambient",
        "crew-ps-fwd-cabin/mood",
        "owners-deckhouse/ambient",
        "owners-deckhouse/mood",
        "main-deckhouse/ambient",
        "main-deckhouse/mood",
        "owners-stairway/main",
        "guest-corridor/main",
        "polynesian-corrido/main",
    }
}

_BLIND_IDS = {
    val: id_to_hass_id(val)
    for val in {
        "owners-cabin/main/shear",
        "owners-cabin/main/blind",
        "owners-cabin/port/shear",
        "owners-cabin/port/blind",
        "owners-cabin/starboard/shear",
        "owners-cabin/starboard/blind",
        "owners-cabin/skyline_main/shear",
        "owners-cabin/skyline_main/blind",
        "owners-cabin/skyline_port/shear",
        "owners-cabin/skyline_port/blind",
        "owners-cabin/skyline_starboard/shear",
        "owners-cabin/skyline_starboard/blind",
        "dutch-cabin/blind",
        "french-cabin/blind",
        "italian-cabin/blind",
        "californian-lounge/blind",
        "polynesian-cabin/blind",
        "galley/blind",
        "crew-mess/blind",
        "mission-room/blind",
        "laundry/blind",
        "engineers-office/blind",
        "captains-cabin/blind",
        "crew-sb-aft-cabin/blind",
        "crew-sb-mid-cabin/blind",
        "crew-sb-fwd-cabin/blind",
        "crew-ps-mid-cabin/blind",
        "crew-ps-fwd-cabin/blind",
        "owners-deckhouse/blind",
        "owners-deckhouse/shear",
        "main-deckhouse/blind",
        "main-deckhouse/shear",
        "owners-stairway/blind",
        "guest-corridor/blind",
    }
}


_LIGHT_GROUP_IDS_INV = invert_dict(_LIGHT_GROUP_IDS)
_BLIND_IDS_INV = invert_dict(_BLIND_IDS)


class Hass:

    def __init__(self, client: HassClient):
        self._client = client

    async def set_lighting_group(self, lighting_group: LightingGroup):
        if lighting_group.id not in _LIGHT_GROUP_IDS:
            raise ValueError(f"unknown lighting group id {lighting_group.id}")
        number = await self._client.async_get_domain("input_number")
        if number is None:
            raise Exception("unable to find input_number domain")
        set_value = number.get_service("set_value")
        if set_value is None:
            raise Exception("unable to find set_value service")
        logger.info(
            f"sending {lighting_group.level} to input_number.{id_to_hass_id(lighting_group.id)}"
        )
        await set_value.async_trigger(
            value=lighting_group.level * 100,  # hass uses 0..100
            entity_id=f"input_number.{id_to_hass_id(lighting_group.id)}",
        )

    async def set_blind(self, blind: Blind):
        if blind.id not in _BLIND_IDS:
            raise ValueError(f"unknown blind id {blind.id}")
        cover = await self._client.async_get_domain("cover")
        if cover is None:
            raise Exception("unable to find cover domain")
        set_cover_position = cover.get_service("set_cover_position")
        if set_cover_position is None:
            raise Exception("unable to find set_cover_position service")
        logger.info(f"sending {blind.level} to cover.{id_to_hass_id(blind.id)}")
        await set_cover_position.async_trigger(
            position=blind.level * 100, entity_id=f"cover.{id_to_hass_id(blind.id)}"
        )

    @asynccontextmanager
    @staticmethod
    async def init_from_settings(settings: Settings):
        client = HassClient(
            settings.home_assistant_url, settings.home_assistant_token, use_async=True
        )
        async with client:
            yield Hass(client)


class InputNumberChangedState(BaseModel):
    entity_id: str
    state: float
    last_changed: datetime
    last_reported: datetime
    last_updated: datetime


class InputNumberChanged(BaseModel):
    entity_id: str
    old_state: InputNumberChangedState
    new_state: InputNumberChangedState

    @property
    def id(self):
        return hass_id_to_id(self.entity_id, "light_group")


class CoverChangeAttributes(BaseModel):
    current_position: int


class CoverChangeState(BaseModel):
    entity_id: str
    attributes: CoverChangeAttributes
    last_changed: datetime
    last_reported: datetime
    last_updated: datetime


class CoverChanged(BaseModel):
    entity_id: str
    old_state: CoverChangeState
    new_state: CoverChangeState

    @property
    def id(self):
        return hass_id_to_id(self.entity_id, "blinds")


class HassControl:

    def __init__(self, hass: HassWsClient, mqtt: Mqtt):
        self._hass = hass
        self._mqtt = mqtt

    # _run is wrapped into run_in_executor to avoid blocking the event loop
    def _run(self, loop: asyncio.AbstractEventLoop):
        with self._hass.listen_events("state_changed") as events:
            for event in events:
                if event.data["entity_id"].startswith("input_number."):
                    number_change = InputNumberChanged(**event.data)
                    if (
                        number_change.id in _LIGHT_GROUP_IDS.keys()
                        and number_change.id is not None
                    ):  # is not None check superfluous, just for type checking
                        lighting_group_msg = LightingGroup(
                            id=number_change.id,
                            level=number_change.new_state.state
                            / 100,  # hass uses 0..100 values
                        )
                        loop.create_task(
                            self._mqtt.send_lighting_group(lighting_group_msg)
                        )
                elif event.data["entity_id"].startswith("cover."):
                    cover_change = CoverChanged(**event.data)
                    if (
                        cover_change.id in _BLIND_IDS.keys()
                    ) and cover_change.id is not None:
                        blind_msg = Blind(
                            id=cover_change.id,
                            level=cover_change.new_state.attributes.current_position
                            / 100,
                        )
                        loop.create_task(self._mqtt.send_blind(blind_msg))

    async def run(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._run, loop)
