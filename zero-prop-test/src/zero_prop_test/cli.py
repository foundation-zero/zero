import asyncio
from contextlib import ExitStack
from datetime import timedelta

from pydantic_settings import BaseSettings, SettingsConfigDict

from zero_prop_test.io_link import ADDRESSES as IOLINK_ADDRESSES
from zero_prop_test.io_link import Client as IoLinkClient
from zero_prop_test.loop import AddressType, Loop
from zero_prop_test.modbus import ADDRESSES as MODBUS_ADDRESSES
from zero_prop_test.modbus import Client as ModbusClient
from zero_prop_test.settings import Settings
from zero_prop_test.twincat import VARIABLES as TWINCAT_VARIABLES
from zero_prop_test.twincat import Client as TwinCatClient
from zero_prop_test.setup_logging import setup_logging


class CliSettings(BaseSettings):
    disable_io_link: bool = False
    disable_modbus: bool = False
    disable_twincat: bool = False
    interval_seconds: float = 1.0

    model_config = SettingsConfigDict(
        extra="ignore",
        cli_parse_args=True,
        cli_implicit_flags=True,
        cli_kebab_case=True,
    )


def _build_addresses(config: CliSettings) -> list[AddressType]:
    addresses: list[AddressType] = []
    if not config.disable_io_link:
        addresses.extend(IOLINK_ADDRESSES)
    if not config.disable_modbus:
        addresses.extend(MODBUS_ADDRESSES)
    if not config.disable_twincat:
        addresses.extend(TWINCAT_VARIABLES)

    return addresses


async def _run() -> None:
    config = CliSettings()
    settings = Settings()  # pyright: ignore[reportCallIssue]
    addresses = _build_addresses(config)
    if not addresses:
        raise ValueError("At least one data source must be enabled")

    iolink_client = (
        IoLinkClient.from_settings(settings) if not config.disable_io_link else None
    )
    modbus_client = (
        ModbusClient.from_settings(settings) if not config.disable_modbus else None
    )

    with ExitStack() as stack:
        twincat_client = (
            stack.enter_context(TwinCatClient.from_settings(settings))
            if not config.disable_twincat
            else None
        )
        loop = Loop.from_settings(
            settings=settings,
            iolink_client=iolink_client,
            modbus_client=modbus_client,
            twincat_client=twincat_client,
            interval=timedelta(seconds=config.interval_seconds),
        )
        await loop.run(addresses)


def main() -> None:
    setup_logging()
    asyncio.run(_run())


if __name__ == "__main__":
    main()
