from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )

    env: Literal["development", "production"] = "development"

    pg_host: str
    pg_port: str
    pg_user: str
    pg_password: str
    pg_db: str

    mqtt_host: str
    mqtt_port: int
    mqtt_username: str | None = None
    mqtt_password: str | None = None

    @property
    def pg_url(self) -> str:
        return f"postgresql+asyncpg://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_db}"

    @property
    def is_development(self) -> bool:
        return self.env == "development"

    @property
    def is_production(self) -> bool:
        return self.env == "production"


settings = Settings()  # type: ignore
