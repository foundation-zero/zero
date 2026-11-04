from secrets import token_hex
from typing import Literal

from pydantic import Field
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
    mqtt_api_client_id: str = Field(default_factory=lambda: f"loads-api-{token_hex(4)}")
    mqtt_control_client_id: str = Field(
        default_factory=lambda: f"loads-control-{token_hex(4)}"
    )
    mqtt_stub_client_id: str = Field(
        default_factory=lambda: f"loads-stub-{token_hex(4)}"
    )
    mqtt_max_message_age_s: float = Field(
        default=30,
        gt=0,
        description="Values from a topic without a message for this long are "
        "reported as missing; set above the slowest re-publish interval (10 s for "
        "the sail system PLC)",
    )

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
