from aiomqtt import Client as MqttClient
from pytest import fixture

from loads.api.db import SessionManager
from loads.config import Settings


async def _mqtt_client(settings):
    async with MqttClient(settings.mqtt_host, settings.mqtt_port) as client:
        yield client


mqtt_client_receive = fixture(_mqtt_client)
mqtt_client_send = fixture(_mqtt_client)
mqtt_client_external = fixture(_mqtt_client)


@fixture
def sessionmanager(settings: Settings):
    sessionmanager = SessionManager()
    sessionmanager.initialize(settings.pg_url)
    return sessionmanager
