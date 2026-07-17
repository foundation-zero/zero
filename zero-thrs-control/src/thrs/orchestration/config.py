from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )
    mqtt_host: str
    mqtt_port: int
    mqtt_devices_topic_prefix: str
    mqtt_controller_topic_prefix: str
    mqtt_controller_topic_suffix: str
    mqtt_simulator_topic_prefix: str
    mqtt_simulator_topic_suffix: str
    mqtt_control_topic_suffix: str

    liveness_path: str | None = None
