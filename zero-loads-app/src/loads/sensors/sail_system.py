from abc import ABC
from typing import Annotated, TypeAlias

from pydantic import BeforeValidator, Field

from .base import LoadsModel
from .units import (
    Alarm as BaseAlarm,
)
from .units import (
    Load as BaseLoad,
)
from .units import (
    Lock,
    ScalingMeta,
    VariableMeta,
    decakilogram_to_tonne,
    per_mille_to_ratio,
    ratio_to_per_mille,
    tonne_to_decakilogram,
)
from .units import (
    MaxLoad as BaseMaxLoad,
)
from .units import (
    Position as BasePosition,
)
from .units import (
    RelativePosition as BaseRelativePosition,
)

Load: TypeAlias = Annotated[  # Needed to be able to override Field constraints where needed (e.g. in Vang). Pydantic has no fixed order to resolve nested `Field`s in inside of `Annotated`s
    BaseLoad,
    Field(validation_alias="st_Load/i_Load"),
    BeforeValidator(decakilogram_to_tonne),
    ScalingMeta(
        conversion=decakilogram_to_tonne,
        inverse_conversion=tonne_to_decakilogram,
    ),
    VariableMeta(name="load"),
]

MaxLoad: TypeAlias = Annotated[
    BaseMaxLoad,
    Field(validation_alias="st_Load/i_MaxLoadSetting"),
    BeforeValidator(decakilogram_to_tonne),
    ScalingMeta(
        conversion=decakilogram_to_tonne,
        inverse_conversion=tonne_to_decakilogram,
    ),
    VariableMeta(threshold_for="load_alarm"),
]

LoadFailure: TypeAlias = Annotated[
    BaseAlarm,
    Field(validation_alias="st_Load/x_Failure"),
    VariableMeta(
        unit="bool", name="load_sensor_failure", type="alarm", alarm_for="load"
    ),
]

LoadAlarm: TypeAlias = Annotated[
    BaseAlarm,
    Field(validation_alias="st_Load/x_MaxLimitReached"),
    VariableMeta(unit="bool", name="max_load_alarm", type="alarm", alarm_for="load"),
]

RelativePosition: TypeAlias = Annotated[
    BaseRelativePosition,
    Field(validation_alias="st_position/i_Position_permille"),
    VariableMeta(name="relative-position"),
    BeforeValidator(per_mille_to_ratio),
    ScalingMeta(
        conversion=per_mille_to_ratio,
        inverse_conversion=ratio_to_per_mille,
    ),
]

Position: TypeAlias = Annotated[
    BasePosition,
    Field(validation_alias="st_position/i_Position_mm"),
    VariableMeta(name="position"),
]

MaxPositionAlarm: TypeAlias = Annotated[
    BaseAlarm,
    Field(validation_alias="st_position/x_MaxLimitReached"),
    VariableMeta(
        name="max-position-alarm", type="alarm", alarm_for="relative_position"
    ),
]

MinPositionAlarm: TypeAlias = Annotated[
    BaseAlarm,
    Field(validation_alias="st_position/x_MinLimitReached"),
    VariableMeta(
        name="min-position-alarm", type="alarm", alarm_for="relative_position"
    ),
]


class PrimaryWinchPs(LoadsModel, ABC):
    TOPIC = "sail-systems/fe212-primary-deck-winch-ps"
    load: Annotated[
        Load,
        VariableMeta(
            display_name="Primary PT",
            applies_to_tack="port",
            variable_key="primary-winch-load",
        ),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad


class PrimaryWinchSb(LoadsModel, ABC):
    TOPIC = "sail-systems/fe308-primary-deck-winch-sb"
    load: Annotated[
        Load,
        VariableMeta(
            display_name="Primary SB",
            applies_to_tack="starboard",
            variable_key="primary-winch-load",
        ),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad


class AftWinchPs(LoadsModel, ABC):
    TOPIC = "sail-systems/fe408-aft-deck-deck-winch-ps"
    load: Annotated[
        Load,
        VariableMeta(
            display_name="Aft Winch PT",
            applies_to_tack="port",
            variable_key="aft-winch-load",
        ),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad


class AftWinchSb(LoadsModel, ABC):
    TOPIC = "sail-systems/fe508-aft-deck-deck-winch-sb"
    load: Annotated[
        Load,
        VariableMeta(
            display_name="Aft Winch SB",
            applies_to_tack="starboard",
            variable_key="aft-winch-load",
        ),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad


class BladeAdjuster(LoadsModel, ABC):
    TOPIC = "sail-systems/f0103-blade-adjuster"
    load: Annotated[Load, VariableMeta(display_name="Adjuster")]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="Adjuster",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]
    max_position_alarm: MaxPositionAlarm
    min_position_alarm: MinPositionAlarm


class BladeCunningham(LoadsModel, ABC):
    TOPIC = "sail-systems/f0101-blade-cunningham"
    load: Annotated[
        Load,
        VariableMeta(
            display_name="Cunningham",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad
    relative_position: Annotated[
        RelativePosition,
        Field(validation_alias="i_PositionAvg_permille"),
        VariableMeta(
            display_name="Cunningham",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]


class BladeSheetFeederPs(LoadsModel, ABC):
    TOPIC = "sail-systems/fe202-blade-sheet-ps-feeder"
    load: Annotated[
        Load,
        VariableMeta(
            display_name="Sheet PT",
            applies_to_tack="port",
            variable_key="blade-sheet-feeder-load",
        ),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad


class BladeSheetFeederSb(LoadsModel, ABC):
    TOPIC = "sail-systems/fe302-blade-sheet-sb-feeder"
    load: Annotated[
        Load,
        VariableMeta(
            display_name="Sheet SB",
            applies_to_tack="starboard",
            variable_key="blade-sheet-feeder-load",
        ),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad


class BladeTweakerPs(LoadsModel, ABC):
    TOPIC = "sail-systems/f0206-blade-tweaker-ps"
    load: Annotated[
        Load,
        VariableMeta(
            display_name="Tweaker PT",
            applies_to_tack="port",
            variable_key="blade-tweaker-load",
        ),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="Tweaker PT",
            scale_min_label="out",
            scale_max_label="in",
            applies_to_tack="port",
            variable_key="blade-tweaker-relative-position",
        ),
    ]
    max_position_alarm: MaxPositionAlarm
    min_position_alarm: MinPositionAlarm


class BladeTweakerSb(LoadsModel, ABC):
    TOPIC = "sail-systems/f0207-blade-tweaker-sb"
    load: Annotated[
        Load,
        VariableMeta(
            display_name="Tweaker SB",
            applies_to_tack="starboard",
            variable_key="blade-tweaker-load",
        ),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="Tweaker SB",
            scale_min_label="out",
            scale_max_label="in",
            applies_to_tack="starboard",
            variable_key="blade-tweaker-relative-position",
        ),
    ]
    max_position_alarm: MaxPositionAlarm
    min_position_alarm: MinPositionAlarm


class CodeZeroTack(LoadsModel, ABC):
    TOPIC = "sail-systems/f0102-code-sail-tack"
    load: Annotated[
        Load,
        VariableMeta(display_name="Tack"),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad
    relative_position: Annotated[
        RelativePosition,
        Field(validation_alias="i_PositionAvg_permille"),
        VariableMeta(
            display_name="Cunningham",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]


class A2Tack(LoadsModel, ABC):
    TOPIC = "sail-systems/a2-tack-placeholder"
    load: Annotated[Load, VariableMeta(display_name="Tack")]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad


class MainHeadstayCombined(LoadsModel, ABC):
    TOPIC = "sail-systems/combined-headstay-placeholder"
    load: Annotated[
        Load,
        VariableMeta(display_name="Headstay Comb"),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad


class Mast(LoadsModel, ABC):
    TOPIC = "sail-systems/mast"
    lock_a2: Annotated[
        Lock,
        Field(validation_alias="ix_SnsrA2Lck"),
        VariableMeta(name="lock_a2", display_name="A2"),
    ]
    overhoist_a2: Annotated[
        Lock,
        Field(validation_alias="ix_SnsrA2LckOvrhst"),
        VariableMeta(name="overhoist_a2", display_name="A2"),
    ]
    lock_a3c0: Annotated[
        Lock,
        Field(validation_alias="ix_SnsrA3C0Lck"),
        VariableMeta(name="lock_a3c0", display_name="A3/C0"),
    ]
    overhoist_a3c0: Annotated[
        Lock,
        Field(validation_alias="ix_SnsrA3C0LckOvrhst"),
        VariableMeta(name="overhoist_a3c0", display_name="A3/C0"),
    ]
    lock_staysail: Annotated[
        Lock,
        Field(validation_alias="ix_SnsrStyslLck"),
        VariableMeta(name="lock_staysail", display_name="Staysail"),
    ]
    overhoist_staysail: Annotated[
        Lock,
        Field(validation_alias="ix_SnsrStyslLckOvrhst"),
        VariableMeta(name="overhoist_staysail", display_name="Staysail"),
    ]
    lock_trysail: Annotated[
        Lock,
        Field(validation_alias="ix_TrysailLck"),
        VariableMeta(name="lock_trysail", display_name="Trysail"),
    ]
    overhoist_trysail: Annotated[
        Lock,
        Field(validation_alias="ix_TrysailOvrhst"),
        VariableMeta(name="overhoist_trysail", display_name="Trysail"),
    ]
    lock_stormjib: Annotated[
        Lock,
        Field(validation_alias="ix_StormJibLck"),
        VariableMeta(name="lock_stormjib", display_name="Storm Jib"),
    ]
    overhoist_stormjib: Annotated[
        Lock,
        Field(validation_alias="ix_StormJibOvrhst"),
        VariableMeta(name="overhoist_stormjib", display_name="Storm Jib"),
    ]

    lock_mizzen_headsail: Annotated[
        Lock,
        Field(validation_alias="F0401_MzznHdFrlr/ix_SnsrHdslLck"),
        VariableMeta(name="lock_mizzen_headsail", display_name="Mizzen Headsail"),
    ]
    overhoist_mizzen_headsail: Annotated[
        Lock,
        Field(validation_alias="F0401_MzznHdFrlr/ix_SnsrHdslLckOvrhst"),
        VariableMeta(name="overhoist_mizzen_headsail", display_name="Mizzen Headsail"),
    ]

    lock_main_1: Annotated[
        Lock,
        Field(validation_alias="FE207_MnHlyrd/ix_SnsrHlyrdLck1"),
        VariableMeta(name="lock_main_1", display_name="Haly Reef 1"),
    ]
    lock_main_2: Annotated[
        Lock,
        Field(validation_alias="FE207_MnHlyrd/ix_SnsrHlyrdLck2"),
        VariableMeta(name="lock_main_2", display_name="Haly Reef 2"),
    ]
    lock_main_3: Annotated[
        Lock,
        Field(validation_alias="FE207_MnHlyrd/ix_SnsrHlyrdLck3"),
        VariableMeta(name="lock_main_3", display_name="Haly Reef 3"),
    ]
    lock_main_headboard: Annotated[
        Lock,
        Field(validation_alias="FE207_MnHlyrd/ix_SnsrHlyrdLckFh"),
        VariableMeta(name="lock_main_headboard", display_name="Haly Headboard"),
    ]
    overhoist_main_1: Annotated[
        Lock,
        Field(validation_alias="FE207_MnHlyrd/ix_SnsrHlyrdLck1Ovrhst"),
        VariableMeta(name="overhoist_main_1", display_name="Haly Reef 1"),
    ]
    overhoist_main_2: Annotated[
        Lock,
        Field(validation_alias="FE207_MnHlyrd/ix_SnsrHlyrdLck2Ovrhst"),
        VariableMeta(name="overhoist_main_2", display_name="Haly Reef 2"),
    ]
    overhoist_main_3: Annotated[
        Lock,
        Field(validation_alias="FE207_MnHlyrd/ix_SnsrHlyrdLck3Ovrhst"),
        VariableMeta(name="overhoist_main_3", display_name="Haly Reef 3"),
    ]
    overhoist_main_headboard: Annotated[
        Lock,
        Field(validation_alias="FE207_MnHlyrd/ix_SnsrHlyrdLckFhOvrhst"),
        VariableMeta(name="overhoist_main_headboard", display_name="Headboard"),
    ]
    lock_main_boom_1: Annotated[
        Lock,
        Field(validation_alias="FE207_MnHlyrd/ix_SnsrBmRfLck1"),
        VariableMeta(name="lock_main_boom_1", display_name="Boom Reef 1"),
    ]
    lock_main_boom_2: Annotated[
        Lock,
        Field(validation_alias="FE207_MnHlyrd/ix_SnsrBmRfLck2"),
        VariableMeta(name="lock_main_boom_2", display_name="Boom Reef 2"),
    ]
    lock_main_boom_3: Annotated[
        Lock,
        Field(validation_alias="FE207_MnHlyrd/ix_SnsrBmRfLck3"),
        VariableMeta(name="lock_main_boom_3", display_name="Boom Reef 3"),
    ]

    lock_mizzen_1: Annotated[
        Lock,
        Field(validation_alias="FE404_MzznHlyrd/ix_SnsrHlyrdLck1"),
        VariableMeta(name="lock_mizzen_1", display_name="Haly Reef 1"),
    ]
    lock_mizzen_2: Annotated[
        Lock,
        Field(validation_alias="FE404_MzznHlyrd/ix_SnsrHlyrdLck2"),
        VariableMeta(name="lock_mizzen_2", display_name="Haly Reef 2"),
    ]
    lock_mizzen_headboard: Annotated[
        Lock,
        Field(validation_alias="FE404_MzznHlyrd/ix_SnsrHlyrdLckFh"),
        VariableMeta(name="lock_mizzen_headboard", display_name="Haly Headboard"),
    ]
    overhoist_mizzen_1: Annotated[
        Lock,
        Field(validation_alias="FE404_MzznHlyrd/ix_SnsrHlyrdLck1Ovrhst"),
        VariableMeta(name="overhoist_mizzen_1", display_name="Haly Reef 1"),
    ]
    overhoist_mizzen_2: Annotated[
        Lock,
        Field(validation_alias="FE404_MzznHlyrd/ix_SnsrHlyrdLck2Ovrhst"),
        VariableMeta(name="overhoist_mizzen_2", display_name="Haly Reef 2"),
    ]
    overhoist_mizzen_headboard: Annotated[
        Lock,
        Field(validation_alias="FE404_MzznHlyrd/ix_SnsrHlyrdLckFhOvrhst"),
        VariableMeta(name="overhoist_mizzen_headboard", display_name="Haly Headboard"),
    ]
    lock_mizzen_boom_1: Annotated[
        Lock,
        Field(validation_alias="FE404_MzznHlyrd/ix_SnsrBmRfLck1"),
        VariableMeta(name="lock_mizzen_boom_1", display_name="Boom Reef 1"),
    ]
    lock_mizzen_boom_2: Annotated[
        Lock,
        Field(validation_alias="FE404_MzznHlyrd/ix_SnsrBmRfLck2"),
        VariableMeta(name="lock_mizzen_boom_2", display_name="Boom Reef 2"),
    ]

    stormjib_load: Annotated[
        Load,
        Field(validation_alias="StormSailFurlerLoad/i_Load"),
        VariableMeta(name="stormjib_load", display_name="Tack"),
    ]
    stormjib_load_failure: Annotated[
        LoadFailure,
        Field(validation_alias="StormSailFurlerLoad/x_Failure"),
        VariableMeta(display_name="Tack Load Failure", alarm_for="stormjib_load"),
    ]
    stormjib_load_alarm: Annotated[
        LoadAlarm,
        Field(validation_alias="StormSailFurlerLoad/x_MaxLimitReached"),
        VariableMeta(alarm_for="stormjib_load"),
    ]
    stormjib_max_load: Annotated[
        MaxLoad,
        Field(validation_alias="StormSailFurlerLoad/i_MaxLoadSetting"),
        VariableMeta(threshold_for="stormjib_load_alarm"),
    ]


class MainCheckstay(LoadsModel, ABC):
    TOPIC = "sail-systems/f0203-main-checkstay-deflector"
    deflector_relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            name="deflector-relative-position",
            display_name="Deflector",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]
    deflector_max_position_alarm: Annotated[
        MaxPositionAlarm,
        VariableMeta(alarm_for="deflector_relative_position"),
    ]
    deflector_min_position_alarm: Annotated[
        MinPositionAlarm,
        VariableMeta(alarm_for="deflector_relative_position"),
    ]
    deflector_load: Annotated[
        Load,
        VariableMeta(name="deflector-load", display_name="Deflector"),
    ]
    deflector_load_failure: Annotated[
        LoadFailure,
        Field(validation_alias="st_Load/x_Failure"),
        VariableMeta(
            name="deflector-load-failure",
            display_name="Checkstay Deflector Load Failure",
            alarm_for="deflector_load",
        ),
    ]
    deflector_load_alarm: Annotated[
        LoadAlarm,
        Field(validation_alias="st_Load/x_MaxLimitReached"),
        VariableMeta(
            name="deflector-load-alarm",
            display_name="Checkstay Deflector Load Alarm",
            alarm_for="deflector_load",
        ),
    ]
    deflector_max_load: Annotated[
        MaxLoad,
        VariableMeta(
            name="deflector-max-load",
            display_name="Checkstay Deflector Max Load",
            threshold_for="deflector_load_alarm",
        ),
    ]

    load_ps: Annotated[
        Load,
        Field(validation_alias="st_LoadPs/i_Load"),
        VariableMeta(
            name="ps-load",
            display_name="Checkstay PT",
            applies_to_tack="port",
            variable_key="main-checkstay-load",
        ),
    ]
    load_sb_failure: Annotated[
        LoadFailure,
        Field(validation_alias="st_LoadSb/x_Failure"),
        VariableMeta(
            name="sb-load-failure",
            display_name="Checkstay SB Load Failure",
            alarm_for="sb_load",
        ),
    ]
    max_load_ps: Annotated[
        MaxLoad,
        VariableMeta(
            name="max-ps-load",
            display_name="Checkstay PT Max Load",
            threshold_for="load_ps_alarm",
        ),
    ]
    load_ps_alarm: Annotated[
        LoadAlarm,
        Field(validation_alias="st_LoadPs/x_MaxLimitReached"),
        VariableMeta(
            name="ps-load-alarm",
            display_name="Checkstay PT Load Alarm",
            alarm_for="ps_load",
        ),
    ]
    load_sb: Annotated[
        Load,
        Field(validation_alias="st_LoadSb/i_Load"),
        VariableMeta(
            name="sb-load",
            display_name="Checkstay SB",
            applies_to_tack="starboard",
            variable_key="main-checkstay-load",
        ),
    ]
    max_load_sb: Annotated[
        MaxLoad,
        VariableMeta(
            name="max-sb-load",
            display_name="Checkstay SB Max Load",
            threshold_for="load_sb_alarm",
        ),
    ]
    load_sb_alarm: Annotated[
        LoadAlarm,
        Field(validation_alias="st_LoadSb/x_MaxLimitReached"),
        VariableMeta(
            name="sb-load-alarm",
            display_name="Checkstay SB Load Alarm",
            alarm_for="sb_load",
        ),
    ]


class MainCunningham(LoadsModel, ABC):
    TOPIC = "sail-systems/f0205-main-cunningham"
    load: Annotated[
        Load,
        VariableMeta(display_name="Cunningham"),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="Cunningham",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]
    max_position_alarm: MaxPositionAlarm
    min_position_alarm: MinPositionAlarm


class MainHalyard(LoadsModel, ABC):
    TOPIC = "sail-systems/fe207-main-halyard-captive-winch"
    load: Annotated[Load, VariableMeta(display_name="Halyard")]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad


class MainOuthaul(LoadsModel, ABC):
    TOPIC = "sail-systems/f0201-main-outhaul"
    load: Annotated[
        Load,
        VariableMeta(display_name="Outhaul"),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="Outhaul", scale_min_label="out", scale_max_label="in"
        ),
    ]
    max_position_alarm: MaxPositionAlarm
    min_position_alarm: MinPositionAlarm


class MainPreventer(LoadsModel, ABC):
    TOPIC = "sail-systems/f0204-main-boom-preventer"
    load: Annotated[
        Load,
        VariableMeta(display_name="Preventer"),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="Preventer",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]
    max_position_alarm: MaxPositionAlarm
    min_position_alarm: MinPositionAlarm


class MainRunnerPs(LoadsModel, ABC):
    TOPIC = "sail-systems/fe401-main-runner-captive-winch-ps"
    load: Annotated[
        Load,
        VariableMeta(
            display_name="Runner PT",
            applies_to_tack="port",
            variable_key="main-runner-load",
        ),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad


class MainRunnerSb(LoadsModel, ABC):
    TOPIC = "sail-systems/fe501-main-runner-captive-winch-sb"
    load: Annotated[
        Load,
        Field(),
        VariableMeta(
            display_name="Runner SB",
            applies_to_tack="starboard",
            variable_key="main-runner-load",
        ),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad


class MainSheet(LoadsModel, ABC):
    TOPIC = "sail-systems/fe205-main-sheet-captive-winch"
    load: Annotated[
        Load,
        Field(),
        VariableMeta(display_name="Sheet"),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad


class MainVang(LoadsModel, ABC):
    TOPIC = "sail-systems/f0202-main-vang"
    load: Annotated[
        Load,
        Field(
            validation_alias="i_Load"
        ),  # Top-level i_Load assumed to be the effective load. st_LoadLc/i_Load is an alternative. Threshold (MaxLoadSetting) not exposed on this topic for ox_LoadAlarm — left open pending clarification.
        VariableMeta(
            display_name="Vang",
            scale_min_label="push",
            scale_max_label="pull",
        ),
    ]
    load_alarm: Annotated[
        LoadAlarm,
        Field(validation_alias="ox_LoadAlarm"),
    ]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(display_name="Vang", scale_min_label="out", scale_max_label="in"),
    ]
    max_position_alarm: MaxPositionAlarm
    min_position_alarm: MinPositionAlarm


class MainTraveller(LoadsModel, ABC):
    TOPIC = "sail-systems/fe405-main-sheet-traveller-winch"
    load: Annotated[Load, VariableMeta(display_name="Traveller")]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad
    relative_position: Annotated[
        RelativePosition,
        Field(
            validation_alias="i_PositionPermille"
        ),  # No underscore, no st_position prefix — inconsistent with st_position/i_Position_permille used elsewhere
        VariableMeta(
            display_name="Traveller",
            scale_min_label="ps",
            scale_max_label="sb",
        ),
    ]
    # TODO: Add position alarms/thresholds (MaxPosition field not found)
    max_position_alarm: MaxPositionAlarm
    min_position_alarm: MinPositionAlarm


class MizzenCheckstay(LoadsModel, ABC):
    TOPIC = "sail-systems/f0503-mizzen-checkstay-deflector"
    deflector_relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            name="deflector-relative-position",
            display_name="Deflector",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]
    deflector_max_position_alarm: Annotated[
        MaxPositionAlarm,
        Field(validation_alias="st_position/x_MaxLimitReached"),
        VariableMeta(
            name="deflector-max-position-alarm",
            display_name="Deflector Max Position Alarm",
            alarm_for="deflector_relative_position",
        ),
    ]
    deflector_min_position_alarm: Annotated[
        MinPositionAlarm,
        Field(validation_alias="st_position/x_MinLimitReached"),
        VariableMeta(
            name="deflector-min-position-alarm",
            display_name="Deflector Min Position Alarm",
            alarm_for="deflector_relative_position",
        ),
    ]

    deflector_load: Annotated[
        Load,
        VariableMeta(name="deflector-load", display_name="Deflector"),
    ]
    deflector_load_failure: Annotated[
        LoadFailure,
        Field(validation_alias="st_Load/x_Failure"),
        VariableMeta(
            name="deflector-load-failure",
            display_name="Deflector Load Failure",
            alarm_for="deflector_load",
        ),
    ]
    deflector_load_alarm: Annotated[
        LoadAlarm,
        Field(validation_alias="st_Load/x_MaxLimitReached"),
        VariableMeta(
            name="deflector-load-alarm",
            display_name="Deflector Load Alarm",
            alarm_for="deflector_load",
        ),
    ]
    deflector_max_load: Annotated[
        MaxLoad,
        Field(validation_alias="st_Load/i_MaxLoadSetting"),
        VariableMeta(
            name="deflector-max-load",
            display_name="Deflector Max Load",
            threshold_for="load_alarm",
        ),
    ]

    load_ps: Annotated[
        Load,
        Field(validation_alias="st_LoadPs/i_Load"),
        VariableMeta(
            name="ps-load",
            display_name="Checkstay PT",
            applies_to_tack="port",
            variable_key="mizzen-checkstay-load",
        ),
    ]
    load_sb_failure: Annotated[
        LoadFailure,
        Field(validation_alias="st_LoadSb/x_Failure"),
        VariableMeta(
            name="sb-load-failure",
            display_name="Checkstay SB Load Failure",
            alarm_for="sb_load",
        ),
    ]
    max_load_ps: Annotated[
        MaxLoad,
        Field(validation_alias="st_LoadPs/i_MaxLoadSetting"),
        VariableMeta(
            name="max-ps-load",
            display_name="Checkstay PT Max Load",
            threshold_for="load_ps_alarm",
        ),
    ]
    load_ps_alarm: Annotated[
        LoadAlarm,
        Field(validation_alias="st_LoadPs/x_MaxLimitReached"),
        VariableMeta(
            name="ps-load-alarm",
            display_name="Checkstay PT Load Alarm",
            alarm_for="ps_load",
        ),
    ]
    load_sb: Annotated[
        Load,
        Field(validation_alias="st_LoadSb/i_Load"),
        VariableMeta(
            name="sb-load",
            display_name="Checkstay SB",
            applies_to_tack="starboard",
            variable_key="mizzen-checkstay-load",
        ),
    ]
    max_load_sb: Annotated[
        MaxLoad,
        Field(validation_alias="st_LoadSb/i_MaxLoadSetting"),
        VariableMeta(
            name="max-sb-load",
            display_name="Checkstay SB Max Load",
            threshold_for="load_sb_alarm",
        ),
    ]
    load_sb_alarm: Annotated[
        LoadAlarm,
        Field(validation_alias="st_LoadSb/x_MaxLimitReached"),
        VariableMeta(
            name="sb-load-alarm",
            display_name="Checkstay SB Load Alarm",
            alarm_for="sb_load",
        ),
    ]


class MizzenCunningham(LoadsModel, ABC):
    TOPIC = "sail-systems/f0504-mizzen-cunningham"
    load: Annotated[
        Load,
        VariableMeta(display_name="Cunningham"),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="Cunningham", scale_min_label="out", scale_max_label="in"
        ),
    ]
    max_position_alarm: MaxPositionAlarm
    min_position_alarm: MinPositionAlarm


class MizzenHalyard(LoadsModel, ABC):
    TOPIC = "sail-systems/fe404-mizzen-halyard-captive-winch"
    load: Annotated[Load, VariableMeta(display_name="Halyard")]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad


class MizzenHeadsailTackAdjuster(LoadsModel, ABC):
    TOPIC = "sail-systems/f0402-mizzen-headsail-tack-adjuster"
    load: Annotated[
        Load,
        VariableMeta(display_name="Adjuster"),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="Adjuster",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]
    max_position_alarm: MaxPositionAlarm
    min_position_alarm: MinPositionAlarm


class MizzenOuthaul(LoadsModel, ABC):
    TOPIC = "sail-systems/f0501-mizzen-outhaul"
    load: Annotated[
        Load,
        VariableMeta(display_name="Outhaul"),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="Outhaul", scale_min_label="out", scale_max_label="in"
        ),
    ]
    max_position_alarm: MaxPositionAlarm
    min_position_alarm: MinPositionAlarm


class MizzenPreventer(LoadsModel, ABC):
    TOPIC = "sail-systems/f0506-mizzen-boom-preventer"
    load: Annotated[
        Load,
        VariableMeta(display_name="Preventer"),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="Preventer",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]
    max_position_alarm: MaxPositionAlarm
    min_position_alarm: MinPositionAlarm


class MizzenRunnerPs(LoadsModel, ABC):
    TOPIC = "sail-systems/fe402-mizzen-runner-captive-winch-ps"
    load: Annotated[
        Load,
        VariableMeta(
            display_name="Runner PT",
            applies_to_tack="port",
            variable_key="mizzen-runner-load",
        ),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad


class MizzenRunnerSb(LoadsModel, ABC):
    TOPIC = "sail-systems/fe502-mizzen-runner-captive-winch-sb"
    load: Annotated[
        Load,
        VariableMeta(
            display_name="Runner SB",
            applies_to_tack="starboard",
            variable_key="mizzen-runner-load",
        ),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad


class MizzenSheet(LoadsModel, ABC):
    TOPIC = "sail-systems/fe504-mizzen-sheet-captive-winch"
    load: Annotated[
        Load,
        VariableMeta(display_name="Sheet"),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad


class MizzenVang(LoadsModel, ABC):
    TOPIC = "sail-systems/f0502-mizzen-vang"
    load: Annotated[
        Load,
        Field(
            validation_alias="i_Load"
        ),  # Top-level i_Load assumed to be the effective load. st_LoadLc/i_Load is an alternative. Threshold (MaxLoadSetting) not exposed on this topic for ox_LoadAlarm — left open pending clarification.
        VariableMeta(
            display_name="Vang",
            scale_min_label="push",
            scale_max_label="pull",
        ),
    ]
    load_alarm: Annotated[
        LoadAlarm,
        Field(validation_alias="ox_LoadAlarm"),
    ]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(display_name="Vang", scale_min_label="out", scale_max_label="in"),
    ]
    max_position_alarm: MaxPositionAlarm
    min_position_alarm: MinPositionAlarm


class StaysailSheetFeederPs(LoadsModel, ABC):
    TOPIC = "sail-systems/fe204-staysail-sheet-ps-feeder"
    load: Annotated[
        Load,
        VariableMeta(
            display_name="Sheet PT",
            applies_to_tack="port",
            variable_key="staysail-sheet-feeder-load",
        ),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad


class StaysailSheetFeederSb(LoadsModel, ABC):
    TOPIC = "sail-systems/fe304-staysail-sheet-sb-feeder"
    load: Annotated[
        Load,
        VariableMeta(
            display_name="Sheet SB",
            applies_to_tack="starboard",
            variable_key="staysail-sheet-feeder-load",
        ),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad


class StaysailStayAdjuster(LoadsModel, ABC):
    TOPIC = "sail-systems/f0104-staysail-stay-adjuster"
    load: Annotated[
        Load,
        VariableMeta(display_name="Adjuster"),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="Adjuster",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]
    max_position_alarm: MaxPositionAlarm
    min_position_alarm: MinPositionAlarm
