import json
import logging
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    CliApp,
    CliPositionalArg,
    CliSubCommand,
    SettingsConfigDict,
)

from zero_atpx_nmea.app import build_app
from zero_atpx_nmea.asyncapi_spec import build_spec

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s"
)


# The chart's probes call /health on this port.
HEALTH_PORT = 8080


class RunCmd(BaseModel):
    async def cli_cmd(self) -> None:
        await build_app().run(
            run_extra_options={
                # uvicorn's default, 127.0.0.1, is out of the kubelet's reach.
                "host": "0.0.0.0",
                "port": HEALTH_PORT,
                # Or every probe is logged. A string: FastStream parses it
                # like a CLI flag.
                "access_log": "false",
            }
        )


class AsyncApiCmd(BaseModel):
    # Emit only the JSON output channels, dropping the raw bare-string input
    # channel. This is the view the MQTT-GraphQL bridge consumes (it builds a
    # schema from object fields, which the raw string channel lacks).
    output_only: bool = False
    output_file: Annotated[
        CliPositionalArg[Path],
        Field(description="File to store the resulting asyncapi"),
    ]

    def cli_cmd(self) -> None:
        with self.output_file.open("w") as result_file:
            json.dump(
                build_spec(include_input_channel=not self.output_only),
                result_file,
                indent=2,
            )


class ZeroAtpxNmea(BaseSettings, cli_kebab_case=True):
    model_config = SettingsConfigDict(
        cli_ignore_unknown_args=True, cli_implicit_flags=True
    )

    run: CliSubCommand[RunCmd]
    generate_asyncapi: CliSubCommand[AsyncApiCmd]

    def cli_cmd(self) -> None:
        try:
            CliApp.run_subcommand(self)
        except KeyboardInterrupt:
            pass
