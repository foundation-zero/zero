"""
Sail system IO list reader.

Parses the CODESYS Symbol Configuration XML export from the Sail PLC to derive
topic/field mappings for MQTT ingestion. Topics are generated as
`sail-systems/{node_name_lowercase}` and fields are the primitive leaf elements
of each node's struct type (compound sub-elements are skipped).

The original hardcoded SAIL_SYSTEM_TOPICS list is retained for comparison
during migration to the XML-driven approach.
"""

import xml.etree.ElementTree as ET
import logging
from pathlib import Path
from typing import List

from polars import DataFrame

from ..base import ReaderBase
from ..types import IOResult, IOTopic, IOValue

logger = logging.getLogger(__name__)

_NS = "http://www.3s-software.com/schemas/Symbolconfiguration.xsd"
_TAG = f"{{{_NS}}}"

# XML typeclass → RisingWave SQL type
_TYPECLASS_TO_SQL: dict[str, str] = {
    "Bool": "BOOLEAN",
    "Int": "INTEGER",
    "UInt": "INTEGER",
    "UDInt": "INTEGER",
    "Word": "INTEGER",
    "Real": "REAL",
}


class SailSystemReader(ReaderBase):
    def read_io_list(self, paths: List[Path]) -> IOResult:
        """Parse CODESYS XML files and return IOResult with all topics."""
        all_topics = [topic for path in paths for topic in self._parse_xml(path)]
        # io_list is only used in io_metadata_marpower
        return IOResult(io_list=DataFrame(), topics=all_topics)

    def _parse_xml(self, path: Path) -> list[IOTopic]:
        """
        Parse a CODESYS Symbol Configuration XML and return one IOTopic per
        HmiData node that has at least one primitive field.

        Topic name: ``sail-systems/{node_name.lower()}``
        Field names: PLC iecname attributes from the struct type definition
        """
        root = ET.parse(path).getroot()
        type_map = self._build_type_map(root)

        hmi_data = root.find(
            f".//{_TAG}Node[@name='Application']/{_TAG}Node[@name='HmiData']"
        )
        if hmi_data is None:
            raise ValueError(f"No Application/HmiData node found in {path}")

        return [
            IOTopic(
                f"sail-systems/{node.get('name', '').lower()}",
                fields,
                group=node.get("type", ""),
            )
            for node in hmi_data.findall(f"{_TAG}Node")
            if (fields := self._collect_fields(node.get("type", ""), type_map))
        ]

    @staticmethod
    def _build_type_map(root: ET.Element) -> dict[str, ET.Element]:
        """Build {type_name -> element} for all TypeSimple and TypeUserDef entries."""
        return {
            name: elem
            for tag in (f"{_TAG}TypeSimple", f"{_TAG}TypeUserDef")
            for elem in root.findall(f"{_TAG}TypeList/{tag}")
            if (name := elem.get("name"))
        }

    @staticmethod
    def _sql_type(
        type_name: str,
        type_map: dict[str, ET.Element],
        _visiting: frozenset[str] = frozenset(),
    ) -> str | None:
        """
        Return the RisingWave SQL type string for a PLC type name.

        Primitive types (TypeSimple) map directly to SQL types.
        Compound types (TypeUserDef) are rendered as STRUCT<field type, ...>,
        recursing into nested structs. Returns None if the type is unknown,
        produces no usable fields, or would form a cycle.
        """
        if type_name in _visiting:
            return None  # break cycle
        elem = type_map.get(type_name)
        if elem is None:
            return None
        if elem.tag == f"{_TAG}TypeSimple":
            typeclass = elem.get("typeclass", "")
            return _TYPECLASS_TO_SQL.get(typeclass)
        if elem.tag == f"{_TAG}TypeUserDef":
            visiting = _visiting | {type_name}
            struct_fields = [
                f"{field_elem.get('iecname')} {sql}"
                for field_elem in elem.findall(f"{_TAG}UserDefElement")
                if field_elem.get("iecname")
                and (
                    sql := SailSystemReader._sql_type(
                        field_elem.get("type", ""), type_map, visiting
                    )
                )
                is not None
            ]
            return f"STRUCT<{', '.join(struct_fields)}>" if struct_fields else None
        return None

    @staticmethod
    def _collect_fields(
        struct_name: str, type_map: dict[str, ET.Element]
    ) -> list[IOValue]:
        """
        Collect all fields from a struct type, including inherited ones.

        Primitive fields map to SQL scalar types; compound sub-elements become
        STRUCT<...> typed fields (recursively). Each UserDefElement child
        (with or without `inherited_from`) is included if its type resolves
        to a non-None SQL type.
        """
        elem = type_map.get(struct_name)
        if elem is None or elem.tag != f"{_TAG}TypeUserDef":
            return []
        return [
            IOValue(field_elem.attrib["iecname"], sql)
            for field_elem in elem.findall(f"{_TAG}UserDefElement")
            if field_elem.get("iecname")
            and (
                sql := SailSystemReader._sql_type(field_elem.get("type", ""), type_map)
            )
            is not None
        ]
