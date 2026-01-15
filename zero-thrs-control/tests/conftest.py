import pytest

from thrs.orchestration.config import Config
import os


@pytest.fixture(scope="session")
def settings():
    os.environ["MQTT_HOST"] = "localhost"

    return Config()  # type: ignore
