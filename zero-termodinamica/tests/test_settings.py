import os

from zero_termodinamica.cli import RunCmd


def test_run_cmd_settings_from_env():
    """Test that RunCmd correctly picks up settings from environment variables without any prefix."""
    os.environ["MODBUS_HOST"] = "127.0.0.1"
    os.environ["MODBUS_PORT"] = "502"
    os.environ["MQTT_HOST"] = "localhost"
    os.environ["MQTT_PORT"] = "1883"

    try:
        settings = RunCmd()
        assert settings.modbus_host == "127.0.0.1"
        assert settings.modbus_port == 502
        assert settings.mqtt_host == "localhost"
        assert settings.mqtt_port == 1883
    finally:
        # Cleanup
        for key in [
            "MODBUS_HOST",
            "MODBUS_PORT",
            "MQTT_HOST",
            "MQTT_PORT",
        ]:
            if key in os.environ:
                del os.environ[key]
