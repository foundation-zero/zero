import json

from zero_domestic_control.config import Settings


def test_config():
    input_config = {
        "jwt_secret": "test_secret",
        "pg_url": "localhost:5432",
        "risingwave_url": "localhost:4566",
        "mqtt_host": "localhost"
    }

    config = Settings.model_validate_json(json.dumps(input_config))
    assert config.jwt_secret == "test_secret"
    assert config.pg_url == "localhost:5432"
    assert config.risingwave_url == "localhost:4566"
    assert config.mqtt_host == "localhost"