"""
Sail system IO list reader.

Derives topic/field mappings from the LoadsModel definitions in zero-loads-app
(loads.sensors.sail_system). PLC sends raw integer values for numeric fields
(decakilograms for loads, per-mille for relative positions) and booleans for
flags. These raw types are stored in RisingWave; conversions happen downstream.
"""

from polars import DataFrame

from zero_data.io_list.types import IOResult, IOTopic, IOValue

# Common reusable field definitions (PLC variable name → RisingWave SQL type)
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


def read_sail_system() -> IOResult:
    """Return sail system topic/field definitions for DBT generation."""
    return IOResult(
        io_list=DataFrame(),
        topics=SAIL_SYSTEM_TOPICS,
    )
