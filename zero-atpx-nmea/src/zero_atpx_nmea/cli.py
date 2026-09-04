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
    def cli_cmd(self) -> None:
        print(json.dumps(build_spec(), indent=2))


class ZeroAtpxNmea(BaseSettings, cli_kebab_case=True):
    model_config = SettingsConfigDict(cli_ignore_unknown_args=True)

    run: CliSubCommand[RunCmd]
    asyncapi: CliSubCommand[AsyncApiCmd]

    def cli_cmd(self) -> None:
        try:
            CliApp.run_subcommand(self)
        except KeyboardInterrupt:
            pass
