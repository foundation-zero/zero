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

from polars import DataFrame

from zero_data.io_list.types import IOResult, IOTopic, IOValue

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


def _build_type_map(root: ET.Element) -> dict[str, ET.Element]:
    """Build {type_name -> element} for all TypeSimple and TypeUserDef entries."""
    type_map: dict[str, ET.Element] = {}
    for elem in root.findall(f"{_TAG}TypeList/{_TAG}TypeSimple"):
        name = elem.get("name")
        if name:
            type_map[name] = elem
    for elem in root.findall(f"{_TAG}TypeList/{_TAG}TypeUserDef"):
        name = elem.get("name")
        if name:
            type_map[name] = elem
    return type_map


def _sql_type(type_name: str, type_map: dict[str, ET.Element]) -> str | None:
    """
    Return the SQL type string for a PLC type name, or None if it is a
    compound struct (which should be skipped as a field).
    """
    elem = type_map.get(type_name)
    if elem is None:
        return None
    if elem.tag == f"{_TAG}TypeSimple":
        typeclass = elem.get("typeclass", "")
        return _TYPECLASS_TO_SQL.get(typeclass)
    # TypeUserDef = compound struct — not a leaf field
    return None


def _collect_fields(struct_name: str, type_map: dict[str, ET.Element]) -> list[IOValue]:
    """
    Collect all primitive leaf fields from a struct type.

    Iterates UserDefElement children (including inherited fields, which are
    listed explicitly in the XML with an `inherited_from` attribute). Compound
    sub-elements (those whose type resolves to another struct) are skipped.
    """
    elem = type_map.get(struct_name)
    if elem is None or elem.tag != f"{_TAG}TypeUserDef":
        return []
    fields: list[IOValue] = []
    for field_elem in elem.findall(f"{_TAG}UserDefElement"):
        iecname = field_elem.get("iecname", "")
        type_name = field_elem.get("type", "")
        sql = _sql_type(type_name, type_map)
        if sql is not None and iecname:
            fields.append(IOValue(iecname, sql))
    return fields


def parse_sail_system_xml(path: Path) -> list[IOTopic]:
    """
    Parse a CODESYS Symbol Configuration XML and return one IOTopic per
    HmiData node that has at least one primitive field.

    Topic name: ``sail-systems/{node_name.lower()}``
    Field names: PLC iecname attributes from the struct type definition
    """
    root = ET.parse(path).getroot()
    type_map = _build_type_map(root)

    hmi_data = root.find(
        f".//{_TAG}Node[@name='Application']/{_TAG}Node[@name='HmiData']"
    )
    if hmi_data is None:
        raise ValueError(f"No Application/HmiData node found in {path}")

    topics: list[IOTopic] = []
    for node in hmi_data.findall(f"{_TAG}Node"):
        name = node.get("name", "")
        plc_type = node.get("type", "")
        fields = _collect_fields(plc_type, type_map)
        if not fields:
            logger.debug(
                f"Skipping node {name!r} (type {plc_type!r}): no primitive fields"
            )
            continue
        topic_name = f"sail-systems/{name.lower()}"
        topics.append(IOTopic(topic_name, fields))
        logger.debug(f"Node {name!r} → {topic_name} ({len(fields)} fields)")

    return topics


# ---------------------------------------------------------------------------
# Original hardcoded list — kept for comparison with the XML-derived output.
# ---------------------------------------------------------------------------

_LOAD = IOValue("ow_ActLoad_10kg", "INTEGER")
_RELIEF_LOAD = IOValue("ow_RelfLoad_10kg", "INTEGER")
_RELATIVE_POSITION = IOValue("relative_position_dummy", "INTEGER")
_ALARM = IOValue("ox_LoadAlarm", "BOOLEAN")

_ADJUSTER_FIELDS = [_LOAD, _RELATIVE_POSITION]
_CUNNINGHAM_FIELDS = [_LOAD, _RELATIVE_POSITION]
_DEFLECTOR_FIELDS = [_RELATIVE_POSITION, _LOAD, _RELIEF_LOAD, _ALARM]
_FEEDER_FIELDS = [_LOAD]
_OUTHAUL_FIELDS = [_LOAD, _RELATIVE_POSITION]
_PREVENTER_FIELDS = [_LOAD, _RELATIVE_POSITION]
_VANG_FIELDS = [_LOAD, _RELATIVE_POSITION]


def _bool(alias: str) -> IOValue:
    return IOValue(alias, "BOOLEAN")


SAIL_SYSTEM_TOPICS: list[IOTopic] = [
    # --- Blade sail ---
    IOTopic("sail-systems/f0103_bldadjstr", _ADJUSTER_FIELDS),  # BladeAdjuster
    IOTopic("sail-systems/f0101_bldcnnnghm", _CUNNINGHAM_FIELDS),  # BladeCunningham
    IOTopic("sail-systems/fe202_bldshtfdrps", _FEEDER_FIELDS),  # BladeSheetFeederPs
    IOTopic("sail-systems/fe302_bldshtfdrsb", _FEEDER_FIELDS),  # BladeSheetFeederSb
    IOTopic("sail-systems/f0206_bldtwkrps", _ADJUSTER_FIELDS),  # BladeTweakerPs
    IOTopic("sail-systems/f0207_bldtwkrsb", _ADJUSTER_FIELDS),  # BladeTweakerSb
    IOTopic("sail-systems/f0102_cdtckcyl", _ADJUSTER_FIELDS),  # CodeZeroTack
    # --- Main sail ---
    IOTopic("sail-systems/f0201_mnothl", _OUTHAUL_FIELDS),  # MainOuthaul
    IOTopic("sail-systems/f0202_mnbmvng", _VANG_FIELDS),  # MainVang
    IOTopic(  # MainCheckstay (Deflector + two extra load channels)
        "sail-systems/f0203_mnchckstydflctr",
        _DEFLECTOR_FIELDS
        + [
            IOValue("i_ActualLoadPs", "INTEGER"),
            IOValue("i_ActualLoadSb", "INTEGER"),
        ],
    ),
    IOTopic("sail-systems/f0204_mnbmprvntr", _PREVENTER_FIELDS),  # MainPreventer
    IOTopic("sail-systems/f0205_mncnnnghm", _CUNNINGHAM_FIELDS),  # MainCunningham
    IOTopic("sail-systems/f0104_stysladjstr", _ADJUSTER_FIELDS),  # StaysailStayAdjuster
    IOTopic(  # HeadsailLocks (fore mast)
        "sail-systems/mnmst",
        [
            _bool("ox_IndctA2Lck_Ext"),
            _bool("ox_IndctA2LckOvrhst_Ext"),
            _bool("ox_IndctA3C0Lck_Ext"),
            _bool("ox_IndctA3C0LckOverhst_Ext"),
            _bool("ox_IndctStyslLck_Ext"),
            _bool("ox_IndctStyslLckOverhst_Ext"),
            _bool("ox_IndctStmjbLck_Ext"),
            _bool("ox_IndctStmjbLckOvrhst_Ext"),
        ],
    ),
    IOTopic(  # MainHalyard
        "sail-systems/fe207_mnhlyrd",
        [
            _LOAD,
            _bool("ox_IndctHlyrdLckFh_Ext"),
            _bool("ox_IndctHlyrdLck1_Ext"),
            _bool("ox_IndctHlyrdLck2_Ext"),
            _bool("ox_IndctHlyrdLck3_Ext"),
            _bool("ox_IndctHlyrdLckFhOvrhst_Ext"),
            _bool("ox_IndctHlyrdLck1Ovrhst_Ext"),
            _bool("ox_IndctHlyrdLck2Ovrhst_Ext"),
            _bool("ox_IndctHlyrdLck3Ovrhst_Ext"),
            _bool("ox_IndctBmRfLck1_Ext"),
            _bool("ox_IndctBmRfLck2_Ext"),
            _bool("ox_IndctBmRfLck3_Ext"),
        ],
    ),
    IOTopic("sail-systems/fe205_mnsht", _FEEDER_FIELDS),  # MainSheet
    IOTopic("sail-systems/fe401_mnrnnrps", _FEEDER_FIELDS),  # MainRunnerPs
    IOTopic("sail-systems/fe501_mnrnnrsb", _FEEDER_FIELDS),  # MainRunnerSb
    IOTopic(  # MainTraveller (relative_position only, range -1..1)
        "sail-systems/fe405_mntrvllr",
        [_RELATIVE_POSITION],
    ),
    # --- Mizzen sail ---
    IOTopic("sail-systems/f0501_mzznothl", _OUTHAUL_FIELDS),  # MizzenOuthaul
    IOTopic("sail-systems/f0502_mzznbmvng", _VANG_FIELDS),  # MizzenVang
    IOTopic(  # MizzenCheckstay (Deflector + two extra load channels)
        "sail-systems/f0503_mzznckstydflctr",
        _DEFLECTOR_FIELDS
        + [
            IOValue("i_ActualLoadPs", "INTEGER"),
            IOValue("i_ActualLoadSb", "INTEGER"),
        ],
    ),
    IOTopic("sail-systems/f0504_mzzncnnnghm", _CUNNINGHAM_FIELDS),  # MizzenCunningham
    IOTopic("sail-systems/f0506_mzznbmprvntr", _PREVENTER_FIELDS),  # MizzenPreventer
    IOTopic(  # MizzenHalyard
        "sail-systems/fe404_mzznhlyrd",
        [
            _LOAD,
            _bool("ox_IndctMzznHlyrdLckFh_Ext"),
            _bool("ox_IndctMzznHlyrdLck1_Ext"),
            _bool("ox_IndctMzznHlyrdLck2_Ext"),
            _bool("ox_IndctMzznHlyrdLckFhOvrhst_Ext"),
            _bool("ox_IndctMzznHlyrdLck1Ovrhst_Ext"),
            _bool("ox_IndctMzznHlyrdLck2Ovrhst_Ext"),
            _bool("ox_IndctMzznBmRfLck1_Ext"),
            _bool("ox_IndctMzznBmRfLck2_Ext"),
        ],
    ),
    IOTopic(  # MizzenHeadsailLocks
        "sail-systems/f0401_mzznhdfrlr",
        [
            _bool("ox_IndctHdslLck_Ext"),
            _bool("ox_IndctHdslLckOvrhst_Ext"),
        ],
    ),
    IOTopic(
        "sail-systems/f0402_mzznhdsladjstr", _ADJUSTER_FIELDS
    ),  # MizzenHeadsailTackAdjuster
    IOTopic("sail-systems/fe402_mzznrnnrps", _FEEDER_FIELDS),  # MizzenRunnerPs
    IOTopic("sail-systems/fe502_mzznrnnrsb", _FEEDER_FIELDS),  # MizzenRunnerSb
    IOTopic("sail-systems/fe504_mzznsht", _FEEDER_FIELDS),  # MizzenSheet
    # --- Staysail ---
    IOTopic(
        "sail-systems/fe204_styslshtfdrps", _FEEDER_FIELDS
    ),  # StaysailSheetFeederPs
    IOTopic(
        "sail-systems/fe304_styslshtfdrsb", _FEEDER_FIELDS
    ),  # StaysailSheetFeederSb
    # --- Winches ---
    IOTopic("sail-systems/fe212_prmrywnchps", _FEEDER_FIELDS),  # PrimaryWinchPs
    IOTopic("sail-systems/fe308_prmrywnchsb", _FEEDER_FIELDS),  # PrimaryWinchSb
    IOTopic("sail-systems/fe408_aftwnchps", _FEEDER_FIELDS),  # AftWinchPs
    IOTopic("sail-systems/fe508_aftwnchsb", _FEEDER_FIELDS),  # AftWinchSb
]

_XML_PATH = Path("io_lists/3094_SailPLC.PLC_MAIN.Application.xml")


def read_sail_system() -> IOResult:
    """Return sail system topic/field definitions for DBT generation.

    Parses the Sail PLC XML export. If the result differs from the hardcoded
    SAIL_SYSTEM_TOPICS (expected during migration), a warning is logged with a
    summary of the differences.
    """
    parsed = parse_sail_system_xml(_XML_PATH)

    if parsed != SAIL_SYSTEM_TOPICS:
        parsed_set = {t.topic for t in parsed}
        legacy_set = {t.topic for t in SAIL_SYSTEM_TOPICS}
        added = parsed_set - legacy_set
        removed = legacy_set - parsed_set
        if added:
            logger.warning(
                f"XML-derived topics not in SAIL_SYSTEM_TOPICS: {sorted(added)}"
            )
        if removed:
            logger.warning(
                f"SAIL_SYSTEM_TOPICS topics not in XML-derived list: {sorted(removed)}"
            )
        logger.warning(
            "Topic/field names differ from legacy SAIL_SYSTEM_TOPICS "
            "(XML uses PLC iecnames; legacy used MQTT aliases). "
            "Update SAIL_SYSTEM_TOPICS or downstream models once validated."
        )

    return IOResult(io_list=DataFrame(), topics=parsed)
