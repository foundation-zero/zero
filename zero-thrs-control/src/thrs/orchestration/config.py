from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )

    pg_host: str | None = None
    pg_port: str | None = None
    pg_user: str | None = None
    pg_password: str | None = None
    pg_db: str | None = None

    mqtt_host: str
    mqtt_port: int
    mqtt_devices_topic_prefix: str
    mqtt_controller_topic_prefix: str
    mqtt_controller_topic_suffix: str
    mqtt_simulator_topic_prefix: str
    mqtt_simulator_topic_suffix: str
    mqtt_control_topic_suffix: str

    liveness_path: str | None = None

    @property
    def pg_url(self) -> str:
        if not all(
            [self.pg_host, self.pg_port, self.pg_user, self.pg_password, self.pg_db]
        ):
            raise ValueError(
                "Postgres configuration is incomplete "
                "(PG_HOST/PG_PORT/PG_USER/PG_PASSWORD/PG_DB)"
            )
        return f"postgresql+asyncpg://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_db}"
