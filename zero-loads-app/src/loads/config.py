from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
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

    canbus_ip: str
    canbus_port: int
    canbus_buffer_size: int

    jwt_secret: str

    @property
    def pg_url(self) -> str:
        return f"postgresql+asyncpg://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_db}"


settings = Settings()  # type: ignore
