from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field


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

    home_assistant_url: str
    home_assistant_ws_url: str
    home_assistant_token: str

    air_conditioning_host: str
    air_conditioning_port: int

    ventilation_host: str
    ventilation_port: int

    jwt_secret: str

    greptime_url: str

    @computed_field  # type: ignore[misc]
    @property
    def pg_url(self) -> str:
        return f"postgresql+psycopg://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_db}"

    @computed_field  # type: ignore[misc]
    @property
    def greptime_url_with_driver(self) -> str:
        return self.greptime_url.replace("mysql", "mysql+aiomysql")


settings = Settings()  # type: ignore
