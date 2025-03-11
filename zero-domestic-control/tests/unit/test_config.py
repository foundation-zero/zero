from pydantic_settings import SettingsConfigDict

from zero_domestic_control.config import Settings


class ConfigTestSettings(Settings):
    model_config = SettingsConfigDict(
        env_file=None, env_prefix="REQUIRE_TEST_TO_CONTAIN_ALL_VALUES"
    )


def test_config():
    input_config = {
        "jwt_secret": "test_secret",
        "pg_host": "localhost",
        "pg_port": "5432",
        "pg_user": "test_user",
        "pg_password": "test_password",
        "pg_db": "test_db",
        "risingwave_url": "localhost:4566",
        "mqtt_host": "localhost",
        "home_assistant_url": "http://localhost:8123/api",
        "home_assistant_ws_url": "ws://localhost:8123/api/websocket",
        "home_assistant_token": "home_assistant_token",
    }

    config = ConfigTestSettings(**input_config)
    assert config.jwt_secret == "test_secret"
    assert config.pg_host == "localhost"
    assert config.pg_port == "5432"
    assert config.pg_user == "test_user"
    assert config.pg_password == "test_password"
    assert config.pg_db == "test_db"
    assert config.risingwave_url == "localhost:4566"
    assert config.mqtt_host == "localhost"
    assert config.home_assistant_url == "http://localhost:8123/api"
    assert config.home_assistant_ws_url == "ws://localhost:8123/api/websocket"
    assert config.home_assistant_token == "home_assistant_token"
