from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )

    pg_host: str
    pg_port: str
    pg_user: str
    pg_password: str
    pg_db: str

    mqtt_host: str
    mqtt_port: int
    mqtt_devices_topic_prefix: str
    mqtt_controller_topic_prefix: str
    mqtt_controller_topic_suffix: str
    mqtt_simulator_topic_prefix: str
    mqtt_simulator_topic_suffix: str
    mqtt_control_topic_suffix: str

    @property
    def pg_url(self) -> str:
        return f"postgresql+asyncpg://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_db}"
