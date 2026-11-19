import pytest

from generator.config import Settings


@pytest.fixture(scope="session")
def settings():
    return Settings(
        mqtt_host="localhost",
        mqtt_port=1883,
    )
