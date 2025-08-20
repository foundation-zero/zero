import asyncio
from fastapi.testclient import TestClient
from pytest import fixture
from homeassistant_api import Client as HassClient, WebsocketClient as HassWsClient
from aiomqtt import Client as MqttClient
from zero_domestic_control.app import app
from zero_domestic_control.config import Settings
from zero_domestic_control.services.hass import Hass, HassControl
from zero_domestic_control.messages import Blind, LightingGroup
from zero_domestic_control.mqtt import DataCollection


@fixture
def settings():
    return Settings()


@fixture
async def hass(settings):
    async with HassClient(
        settings.home_assistant_url, settings.home_assistant_token, use_async=True
    ) as client:
        yield client


@fixture
def hass_ws(settings):
    with HassWsClient(
        settings.home_assistant_ws_url, settings.home_assistant_token
    ) as client:
        yield client


@fixture
async def mqtt(settings):
    async with MqttClient(settings.mqtt_host, settings.mqtt_port) as client:
        yield client


mqtt_two = mqtt


def test_version():
    client = TestClient(app)
    response = client.post("/graphql", json={"query": "query { version }"})

    assert response.status_code == 200
    assert response.json() == {"data": {"version": "1.0.0"}}


async def test_lighting_group_to_hass(hass):
    client = TestClient(app)
    response = client.post(
        "/graphql",
        json={
            "query": """mutation { setLightingGroups(ids: "owners-cabin/mood", level: 0.5) { code success message } }"""
        },
    )

    assert response.status_code == 200

    light = await hass.async_get_entity(entity_id="input_number.owners_cabin_mood")
    assert light.state.state == "50.0"


async def test_hass_lighting_group_to_control_to_mqtt(
    mqtt: MqttClient, mqtt_two: MqttClient, hass_ws, hass
):
    mqtt_wrapper = DataCollection(mqtt)
    control = HassControl(hass_ws, mqtt_wrapper)

    hass_wrapped = Hass(hass)

    control_task = asyncio.create_task(control.run())

    # ensure lighting changes in the actual call, if not different, hass doesn't trigger
    diff_msg = LightingGroup(id="owners-cabin/mood", level=0.1)
    await hass_wrapped.set_lighting_group(diff_msg)
    await asyncio.sleep(0.1)

    await mqtt_two.subscribe("domestic/lighting-groups")
    msg = LightingGroup(id="owners-cabin/mood", level=0.5)
    await hass_wrapped.set_lighting_group(msg)
    await asyncio.sleep(0.2)

    result = await anext(mqtt_two.messages)
    if LightingGroup.model_validate_json(result.payload).level == 0.1:
        result = await anext(mqtt_two.messages)
    if LightingGroup.model_validate_json(result.payload).level == 0.1:
        result = await anext(mqtt_two.messages)

    assert result.topic.value == "domestic/lighting-groups"
    assert LightingGroup.model_validate_json(result.payload) == msg

    control_task.cancel()


async def test_blind_to_hass(hass):
    client = TestClient(app)
    response = client.post(
        "/graphql",
        json={
            "query": """mutation { setBlinds(ids: "owners-cabin/main/shear", level: 0.5) { code success message } }"""
        },
    )

    assert response.status_code == 200

    blind = await hass.async_get_entity(entity_id="cover.owners_cabin_main_shear")
    print(blind.state.attributes)
    assert blind.state.attributes["current_position"] == 50.0


async def test_hass_blind_to_control_to_mqtt(
    mqtt: MqttClient, mqtt_two: MqttClient, hass_ws, hass
):
    mqtt_wrapper = DataCollection(mqtt)
    control = HassControl(hass_ws, mqtt_wrapper)

    hass_wrapped = Hass(hass)

    control_task = asyncio.create_task(control.run())

    # ensure lighting changes in the actual call, if not different, hass doesn't trigger
    diff_msg = Blind(id="owners-cabin/main/shear", level=0.1)
    await hass_wrapped.set_blind(diff_msg)
    await asyncio.sleep(0.2)

    await mqtt_two.subscribe("domestic/blinds")
    msg = Blind(id="owners-cabin/main/shear", level=0.5)
    await hass_wrapped.set_blind(msg)

    result = await anext(mqtt_two.messages)
    if Blind.model_validate_json(result.payload).level == 0.1:
        result = await anext(mqtt_two.messages)
    if Blind.model_validate_json(result.payload).level == 0.1:
        result = await anext(mqtt_two.messages)

    assert result.topic.value == "domestic/blinds"
    assert Blind.model_validate_json(result.payload) == msg

    control_task.cancel()
