# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "aiomqtt",
#     "httpx",
#     "pydantic-settings",
# ]
# ///

import asyncio
import json
import logging
from datetime import datetime, timezone

import aiomqtt
import httpx
from pydantic_settings import BaseSettings, SettingsConfigDict

topic_mapping = {
    "marpower/150000propulsion/pcs-fwd" : "marpower__150000propulsion__pcs_fwd2"
}



class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )
    mqtt_host: str
    mqtt_port: int
    mqtt_user: str
    mqtt_password: str

    greptimedb_host: str
    greptimedb_port: int


async def subscribe_and_ingest(
    mqtt_client: aiomqtt.Client,
    http_client: httpx.AsyncClient,
    settings: Settings,
    logger: logging.Logger,
) -> None:
    """Subscribes to all topics in topic_mapping and ingests received messages into GreptimeDB."""
    # Subscribe to all topics (keys of topic_mapping)
    for topic in topic_mapping.keys():
        logger.info(f"Subscribing to MQTT topic: '{topic}'")
        await mqtt_client.subscribe(topic)

    logger.info("Successfully subscribed to all topics. Listening for messages...")

    # Process incoming MQTT messages
    async for message in mqtt_client.messages:
        topic = str(message.topic)
        table_name = topic_mapping.get(topic)
        if not table_name:
            logger.warning(f"No table mapping found for topic: '{topic}'")
            continue

        # Decode payload
        try:
            payload_str = (
                message.payload.decode("utf-8")
                if isinstance(message.payload, bytes)
                else str(message.payload)
            )
            data = json.loads(payload_str)
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            logger.error(f"Failed to decode or parse JSON from message on topic '{topic}': {e}")
            continue

        if not isinstance(data, dict):
            logger.warning(f"Parsed JSON payload is not a dictionary on topic '{topic}': {data}")
            continue


        max_timestamp = None
        for _, value in data.items():
            if "Timestamp" in value:
                timestamp = datetime.fromisoformat(value["TimeStamp"])
                if max_timestamp is None or timestamp > max_timestamp:
                    max_timestamp = timestamp

        # Prepare the ingestion URL
        ingest_url = f"http://{settings.greptimedb_host}:{settings.greptimedb_port}/v1/ingest"
        params = {"table": table_name, "db": "public","pipeline_name": "greptime_identity"}
        headers = {"Content-Type": "application/json"}

        try:
            # Ingest into GreptimeDB via HTTP
            response = await http_client.post(
                ingest_url,
                params=params,
                headers=headers,
                json=data,
                timeout=5.0
            )
            response.raise_for_status()
            logger.info(f"Successfully ingested message from '{topic}' into table '{table_name}'")
        except httpx.HTTPError as http_err:
            logger.error(f"HTTP error during ingestion for topic '{topic}': {http_err}")
            # We raise to trigger the outer reconnection logic if it's a persistent issue
            raise
        except Exception as e:
            logger.error(f"Unexpected error during ingestion for topic '{topic}': {e}")


async def main() -> None:
    """Configures logging, manages connection lifecycle, and handles reconnection upon error."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger = logging.getLogger("data_ingest")

    settings = Settings()

    retry_interval = 5.0

    while True:
        try:
            logger.info("Initializing HTTP and MQTT clients...")

            # Initialize HTTP client once outside the loop
            async with httpx.AsyncClient() as http_client:
                # Establish the MQTT broker connection
                async with aiomqtt.Client(
                    hostname=settings.mqtt_host,
                    port=settings.mqtt_port,
                    username=settings.mqtt_user,
                    password=settings.mqtt_password,
                ) as mqtt_client:
                    logger.info("Connected to MQTT Broker.")

                    # Hand off to the subscription and ingestion loop
                    await subscribe_and_ingest(mqtt_client, http_client, settings, logger)

        except (aiomqtt.MqttError, httpx.HTTPError, Exception) as err:
            logger.error(f"Error occurred: {err}")
            raise

        logger.info(f"Reconnecting in {retry_interval} seconds...")
        await asyncio.sleep(retry_interval)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown requested by user. Exiting gracefully.")
