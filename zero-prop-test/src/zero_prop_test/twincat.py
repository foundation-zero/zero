from contextlib import contextmanager
import logging
from typing import Any, Generator
from xml.etree import ElementTree

from attr import dataclass
from pyads import (
    Connection,
    set_local_address,
)

from zero_prop_test.settings import TwinCatSettings


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Variable:
    name: str
    type: str

    @property
    def is_primitive(self) -> bool:
        return self.type in {"INT", "REAL", "BOOL", "STRING"}


class TwincatProject:
    def __init__(self, text: str):
        self._tree = ElementTree.fromstring(text)

    def _get_element_text(self, element: ElementTree.Element, tag: str) -> str:
        child_element = element.find(tag)
        if child_element is None:
            raise ValueError(f"Symbol element does not contain a {tag} element.")
        if child_element.text is None:
            raise ValueError(f"{tag} element does not contain text.")
        return child_element.text

    def _variable_name(self, symbol_element: ElementTree.Element) -> str:
        return self._get_element_text(symbol_element, "Name")

    def _variable_type(self, symbol_element: ElementTree.Element) -> str:
        return self._get_element_text(symbol_element, "Type")

    def variables(self) -> set[Variable]:
        symbols = self._tree.find("Symbols")
        if symbols is None:
            logger.warning("No Symbols section found in TwinCAT project XML.")
            return set()
        symbol_elements = symbols.findall("Symbol")
        return {
            Variable(name=self._variable_name(symbol), type=self._variable_type(symbol))
            for symbol in symbol_elements
        }

    @staticmethod
    def variables_from_settings(settings: TwinCatSettings) -> set[Variable]:
        with open("plc.tpy", "r") as f:
            project = TwincatProject(f.read())
            return {
                variable
                for variable in project.variables()
                if variable.is_primitive
                and any(
                    variable.name.startswith(prefix)
                    for prefix in settings.twincat_prefices
                )
            }


class Client:
    def __init__(self, plc: Connection):
        self._plc = plc

    @contextmanager
    @staticmethod
    def from_settings(settings: TwinCatSettings) -> "Generator[Client, None, None]":
        set_local_address(settings.twincat_self_netid)
        logger.info(
            f"Connecting to TwinCAT PLC {settings.twincat_netid}. Local address: {settings.twincat_self_netid}, settings: {settings}"
        )
        plc = Connection(
            settings.twincat_netid,
            settings.twincat_port,
            settings.twincat_ip,
        )
        plc.set_timeout(1000)
        logger.info("Built PLC object")
        with plc:
            logger.info(
                f"Connected to TwinCAT PLC {settings.twincat_netid}. Local address: {plc.get_local_address()}"
            )
            yield Client(plc)

    def query(self, variable: Variable) -> Any:
        logger.debug(f"Querying TwinCAT variable: {variable.name}")
        try:
            res = self._plc.read_by_name(variable.name)
        except Exception as e:
            logger.debug(f"Error querying TwinCAT variable {variable.name}: {e}")
            res = None
        logger.debug(f"Received value from TwinCAT: {res}")
        return res
