import os

import pytest

from thrs.graphql.strawberry import create_app
from thrs.orchestration.config import Config


@pytest.fixture(scope="session")
def settings():
    os.environ["MQTT_HOST"] = "localhost"
    os.environ["MQTT_DEVICES_TOPIC_PREFIX"] = "thrs"

    return Config()  # type: ignore


@pytest.fixture(scope="session")
def app(settings):
    return create_app(settings)
