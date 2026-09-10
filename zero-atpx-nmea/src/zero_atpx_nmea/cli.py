import json
import logging

from pydantic import BaseModel
from pydantic_settings import BaseSettings, CliApp, CliSubCommand, SettingsConfigDict

from zero_atpx_nmea.app import build_app
from zero_atpx_nmea.asyncapi_spec import build_spec

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s"
)


class RunCmd(BaseModel):
    async def cli_cmd(self) -> None:
        await build_app().run()


class AsyncApiCmd(BaseModel):
    # Emit only the JSON output channels, dropping the raw bare-string input
    # channel. This is the view the MQTT-GraphQL bridge consumes (it builds a
    # schema from object fields, which the raw string channel lacks).
    output_only: bool = False

    def cli_cmd(self) -> None:
        print(
            json.dumps(build_spec(include_input_channel=not self.output_only), indent=2)
        )


class ZeroAtpxNmea(BaseSettings, cli_kebab_case=True):
    model_config = SettingsConfigDict(
        cli_ignore_unknown_args=True, cli_implicit_flags=True
    )

    run: CliSubCommand[RunCmd]
    asyncapi: CliSubCommand[AsyncApiCmd]

    def cli_cmd(self) -> None:
        try:
            CliApp.run_subcommand(self)
        except KeyboardInterrupt:
            pass
