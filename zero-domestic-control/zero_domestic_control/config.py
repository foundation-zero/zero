from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )

    jwt_secret: str

    pg_host: str
    pg_port: str
    pg_user: str
    pg_password: str
    pg_db: str

    risingwave_url: str

    mqtt_host: str
    mqtt_port: int

    home_assistant_url: str
    home_assistant_ws_url: str
    home_assistant_token: str

    termodinamica_host: str
    termodinamica_port: int

    @property
    def pg_url(self) -> str:
        return f"postgresql://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_db}"
