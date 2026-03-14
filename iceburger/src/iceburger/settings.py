from typing import Literal

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    rabbitmq_host: str
    rabbitmq_port: int = 5672
    rabbitmq_username: str
    rabbitmq_password: str
    iceberg_catalog_type: Literal["sql", "rest"]
    iceberg_catalog_uri: str
    iceberg_warehouse: str
    iceberg_namespace: str
    s3_endpoint: str
    s3_access_key_id: str
    s3_secret_access_key: str
    s3_region: str

    sink_workers: int = 30

    config_path: str = "config.yaml"


class RoutingConfig(BaseModel):
    routing_key_prefix: str
    table: str
    timestamp: bool
    exclude_routing_key: bool = False


class BatchConfig(BaseModel):
    size: int = 10_000
    seconds: int = 60


class AmqpConfig(BaseModel):
    exchange: str
    queue: str
    routing_keys: list[str]


class Config(BaseModel):
    batch: BatchConfig
    amqp: AmqpConfig
    routings: list[RoutingConfig]
