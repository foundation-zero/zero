from contextlib import ExitStack
from datetime import timedelta

from pydantic import BaseModel
from pydantic_settings import BaseSettings, CliApp, CliSubCommand, SettingsConfigDict

from zero_prop_test.io_link import ADDRESSES as IOLINK_ADDRESSES
from zero_prop_test.io_link import Client as IoLinkClient
from zero_prop_test.loop import AddressType, Loop
from zero_prop_test.modbus import ADDRESSES as MODBUS_ADDRESSES
from zero_prop_test.modbus import Client as ModbusClient
from zero_prop_test.settings import Settings, TwinCatOnlySettings, TwinCatSettings
from zero_prop_test.setup_logging import setup_logging
from zero_prop_test.twincat import Client as TwinCatClient, TwincatProject


class RunCommand(BaseModel):
    disable_io_link: bool = False
    disable_modbus: bool = False
    disable_twincat: bool = False
    interval_seconds: float = 1.0

    async def cli_cmd(self) -> None:
        settings = Settings()  # pyright: ignore[reportCallIssue]
        addresses = self._build_addresses(settings)
        if not addresses:
            raise ValueError("At least one data source must be enabled")

        iolink_client = (
            IoLinkClient.from_settings(settings) if not self.disable_io_link else None
        )
        modbus_client = (
            ModbusClient.from_settings(settings) if not self.disable_modbus else None
        )

        with ExitStack() as stack:
            twincat_client = (
                stack.enter_context(TwinCatClient.from_settings(settings))
                if not self.disable_twincat
                else None
            )
            async with Loop.from_settings(
                settings=settings,
                iolink_client=iolink_client,
                modbus_client=modbus_client,
                twincat_client=twincat_client,
                interval=timedelta(seconds=self.interval_seconds),
            ) as loop:
                await loop.run(addresses)

    def _build_addresses(self, settings: TwinCatSettings) -> list[AddressType]:
        addresses: list[AddressType] = []
        if not self.disable_io_link:
            addresses.extend(IOLINK_ADDRESSES)
        if not self.disable_modbus:
            addresses.extend(MODBUS_ADDRESSES)
        if not self.disable_twincat:
            addresses.extend(TwincatProject.variables_from_settings(settings))
        return addresses


class TwinCatCommand(BaseModel):
    interval_seconds: float = 1.0

    async def cli_cmd(self) -> None:
        settings = TwinCatOnlySettings()  # pyright: ignore[reportCallIssue]
        addresses = list(TwincatProject.variables_from_settings(settings))
        with TwinCatClient.from_settings(settings) as twincat_client:
            async with Loop.from_settings(
                settings=settings,
                twincat_client=twincat_client,
                interval=timedelta(seconds=self.interval_seconds),
            ) as loop:
                await loop.run(addresses)


class App(BaseSettings):
    model_config = SettingsConfigDict(
        cli_kebab_case=True,
        cli_implicit_flags=True,
    )

    run: CliSubCommand[RunCommand]
    twincat: CliSubCommand[TwinCatCommand]

    def cli_cmd(self) -> None:
        CliApp.run_subcommand(self)


def main() -> None:
    setup_logging()
    CliApp.run(App)


if __name__ == "__main__":
    main()
