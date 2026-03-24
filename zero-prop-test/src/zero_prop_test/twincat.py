from contextlib import contextmanager
import logging
from typing import Any, Generator

from attr import dataclass
from pyads import (
    Connection,
    PORT_TC3PLC1,
    set_local_address,
)

from zero_prop_test.settings import Settings


logger = logging.getLogger(__name__)


class Client:
    def __init__(self, plc: Connection):
        self._plc = plc

    @contextmanager
    @staticmethod
    def from_settings(settings: Settings) -> "Generator[Client, None, None]":
        set_local_address(settings.twincat_self_netid)
        plc = Connection(
            settings.twincat_netid,
            PORT_TC3PLC1,
            settings.twincat_ip,
        )
        with plc:
            logger.info(
                f"Connected to TwinCAT PLC {settings.twincat_netid}. Local address: {plc.get_local_address()}"
            )
            yield Client(plc)

    def query(self, variable: "TwinCatVariable") -> Any:
        logger.debug(f"Querying TwinCAT variable: {variable.name}")
        res = self._plc.read_by_name(variable.name)
        logger.debug(f"Received value from TwinCAT: {res}")
        return res


@dataclass(frozen=True)
class TwinCatVariable:
    name: str


# TODO: Add variables once we receive them
VARIABLES = {TwinCatVariable(name="GVL.test")}
