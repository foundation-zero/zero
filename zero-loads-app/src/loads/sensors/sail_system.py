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
    Field(ge=0, validation_alias="st_Load/i_MaxLoadSetting"),
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
        Field(ge=0, le=15),
        VariableMeta(display_name="Primary PT", scale_min=0, scale_max=15),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad


class PrimaryWinchSb(LoadsModel, ABC):
    TOPIC = "sail-systems/fe308-primary-deck-winch-sb"
    load: Annotated[
        Load,
        Field(ge=0, le=15),
        VariableMeta(display_name="Primary SB", scale_min=0, scale_max=15),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad


class AftWinchPs(LoadsModel, ABC):
    TOPIC = "sail-systems/fe408-aft-deck-deck-winch-ps"
    load: Annotated[
        Load,
        Field(ge=0, le=9),
        VariableMeta(display_name="Aft Winch PT", scale_min=0, scale_max=9),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad


class AftWinchSb(LoadsModel, ABC):
    TOPIC = "sail-systems/fe508-aft-deck-deck-winch-sb"
    load: Annotated[
        Load,
        Field(ge=0, le=9),
        VariableMeta(display_name="Aft Winch SB", scale_min=0, scale_max=9),
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
        Field(
            validation_alias="st_positionPs/i_Position_permille"
        ),  # TODO: taking ps as default, t avg pos should be added
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
        Field(ge=0, le=20),
        VariableMeta(display_name="Sheet PT", scale_min=0, scale_max=20),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad


class BladeSheetFeederSb(LoadsModel, ABC):
    TOPIC = "sail-systems/fe302-blade-sheet-sb-feeder"
    load: Annotated[
        Load,
        Field(ge=0, le=20),
        VariableMeta(display_name="Sheet SB", scale_min=0, scale_max=20),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad


class BladeTweakerPs(LoadsModel, ABC):
    TOPIC = "sail-systems/f0206-blade-tweaker-ps"
    load: Annotated[
        Load,
        Field(ge=0, le=15),
        VariableMeta(display_name="Tweaker PT", scale_min=0, scale_max=15),
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
        ),
    ]
    max_position_alarm: MaxPositionAlarm
    min_position_alarm: MinPositionAlarm


class BladeTweakerSb(LoadsModel, ABC):
    TOPIC = "sail-systems/f0207-blade-tweaker-sb"
    load: Annotated[
        Load,
        Field(ge=0, le=15),
        VariableMeta(display_name="Tweaker SB", scale_min=0, scale_max=15),
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
        ),
    ]
    max_position_alarm: MaxPositionAlarm
    min_position_alarm: MinPositionAlarm


class CodeZeroTack(LoadsModel, ABC):
    TOPIC = "sail-systems/f0102-code-sail-tack"
    load: Annotated[
        Load,
        Field(ge=0, le=33),
        VariableMeta(display_name="Tack", scale_min=0, scale_max=33),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad
    relative_position: Annotated[
        RelativePosition,
        Field(
            validation_alias="st_positionPs/i_Position_permille"
        ),  # TODO: taking ps as default, but avg pos should be added
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
        Field(ge=0, le=66),
        VariableMeta(display_name="Headstay Combined", scale_min=0, scale_max=66),
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
    lock_stormjib: Annotated[
        Lock,
        Field(validation_alias="ix_SnsrSrmJpLck"),
        VariableMeta(name="lock_stormjib", display_name="Storm Jib"),
    ]
    overhoist_stormjib: Annotated[
        Lock,
        Field(validation_alias="ix_SnsrSrmJpLckOvrhst"),
        VariableMeta(name="overhoist_stormjib", display_name="Storm Jib"),
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

    main_lock_1: Annotated[
        Lock,
        Field(validation_alias="FE207_MnHlyrd/ix_SnsrHlyrdLck1"),
        VariableMeta(name="main_lock_1", display_name="Main Halyard Reef 1"),
    ]
    main_lock_2: Annotated[
        Lock,
        Field(validation_alias="FE207_MnHlyrd/ix_SnsrHlyrdLck2"),
        VariableMeta(name="main_lock_2", display_name="Main Halyard Reef 2"),
    ]
    main_lock_3: Annotated[
        Lock,
        Field(validation_alias="FE207_MnHlyrd/ix_SnsrHlyrdLck3"),
        VariableMeta(name="main_lock_3", display_name="Main Halyard Reef 3"),
    ]
    main_lock_full: Annotated[
        Lock,
        Field(validation_alias="FE207_MnHlyrd/ix_SnsrHlyrdLckFh"),
        VariableMeta(name="main_lock_full", display_name="Main Halyard Masthead"),
    ]
    main_overhoist_1: Annotated[
        Lock,
        Field(validation_alias="FE207_MnHlyrd/ix_SnsrHlyrdLck1Ovrhst"),
        VariableMeta(name="main_overhoist_1", display_name="Main Halyard Reef 1"),
    ]
    main_overhoist_2: Annotated[
        Lock,
        Field(validation_alias="FE207_MnHlyrd/ix_SnsrHlyrdLck2Ovrhst"),
        VariableMeta(name="main_overhoist_2", display_name="Main Halyard Reef 2"),
    ]
    main_overhoist_3: Annotated[
        Lock,
        Field(validation_alias="FE207_MnHlyrd/ix_SnsrHlyrdLck3Ovrhst"),
        VariableMeta(name="main_overhoist_3", display_name="Main Halyard Reef 3"),
    ]
    main_overhoist_full: Annotated[
        Lock,
        Field(validation_alias="FE207_MnHlyrd/ix_SnsrHlyrdLckFhOvrhst"),
        VariableMeta(name="main_overhoist_full", display_name="Main Halyard Masthead"),
    ]
    main_boom_lock_1: Annotated[
        Lock,
        Field(validation_alias="FE207_MnHlyrd/ix_SnsrBmRfLck1"),
        VariableMeta(name="main_boom_lock_1", display_name="Main Boom 1"),
    ]
    main_boom_lock_2: Annotated[
        Lock,
        Field(validation_alias="FE207_MnHlyrd/ix_SnsrBmRfLck2"),
        VariableMeta(name="main_boom_lock_2", display_name="Main Boom 2"),
    ]
    main_boom_lock_3: Annotated[
        Lock,
        Field(validation_alias="FE207_MnHlyrd/ix_SnsrBmRfLck3"),
        VariableMeta(name="main_boom_lock_3", display_name="Main Boom 3"),
    ]

    mizzen_lock_1: Annotated[
        Lock,
        Field(validation_alias="FE404_MzznHlyrd/ix_SnsrHlyrdLck1"),
        VariableMeta(name="mizzen_lock_1", display_name="Mizzen Halyard Reef 1"),
    ]
    mizzen_lock_2: Annotated[
        Lock,
        Field(validation_alias="FE404_MzznHlyrd/ix_SnsrHlyrdLck2"),
        VariableMeta(name="mizzen_lock_2", display_name="Mizzen Halyard Reef 2"),
    ]
    mizzen_lock_full: Annotated[
        Lock,
        Field(validation_alias="FE404_MzznHlyrd/ix_SnsrHlyrdLckFh"),
        VariableMeta(name="mizzen_lock_full", display_name="Mizzen Halyard Masthead"),
    ]
    mizzen_overhoist_1: Annotated[
        Lock,
        Field(validation_alias="FE404_MzznHlyrd/ix_SnsrHlyrdLck1Ovrhst"),
        VariableMeta(name="mizzen_overhoist_1", display_name="Mizzen Halyard Reef 1"),
    ]
    mizzen_overhoist_2: Annotated[
        Lock,
        Field(validation_alias="FE404_MzznHlyrd/ix_SnsrHlyrdLck2Ovrhst"),
        VariableMeta(name="mizzen_overhoist_2", display_name="Mizzen Halyard Reef 2"),
    ]
    mizzen_overhoist_full: Annotated[
        Lock,
        Field(validation_alias="FE404_MzznHlyrd/ix_SnsrHlyrdLckFhOvrhst"),
        VariableMeta(
            name="mizzen_overhoist_full", display_name="Mizzen Halyard Masthead"
        ),
    ]
    mizzen_boom_lock_1: Annotated[
        Lock,
        Field(validation_alias="FE404_MzznHlyrd/ix_SnsrBmRfLck1"),
        VariableMeta(name="mizzen_boom_lock_1", display_name="Mizzen Boom 1"),
    ]
    mizzen_boom_lock_2: Annotated[
        Lock,
        Field(validation_alias="FE404_MzznHlyrd/ix_SnsrBmRfLck2"),
        VariableMeta(name="mizzen_boom_lock_2", display_name="Mizzen Boom 2"),
    ]

    storm_jib_load: Annotated[
        Load,
        Field(ge=0, le=30, validation_alias="StormSailFurlerLoad/i_Load"),
        VariableMeta(
            name="storm_jib_load", display_name="Tack", scale_min=0, scale_max=30
        ),
    ]
    storm_jib_load_failure: Annotated[
        LoadFailure,
        Field(validation_alias="StormSailFurlerLoad/x_Failure"),
        VariableMeta(display_name="Tack Load Failure", alarm_for="storm_jib_load"),
    ]
    storm_jib_load_alarm: Annotated[
        LoadAlarm,
        Field(validation_alias="StormSailFurlerLoad/x_MaxLimitReached"),
        VariableMeta(alarm_for="storm_jib_load"),
    ]
    storm_jib_max_load: Annotated[
        MaxLoad,
        Field(validation_alias="StormSailFurlerLoad/i_MaxLoadSetting"),
        VariableMeta(threshold_for="storm_jib_load_alarm"),
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
        Field(ge=0, le=8),
        VariableMeta(
            name="deflector-load", display_name="Deflector", scale_min=0, scale_max=8
        ),
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
        Field(validation_alias="st_Load/i_MaxLoad", ge=0, le=8),
        VariableMeta(
            name="deflector-max-load",
            display_name="Checkstay Deflector Max Load",
            scale_min=0,
            scale_max=8,
            threshold_for="deflector_load_alarm",
        ),
    ]

    load_ps: Annotated[
        Load,
        Field(validation_alias="st_LoadPs/i_Load", ge=0, le=15),
        VariableMeta(
            name="ps-load", display_name="Checkstay PT", scale_min=0, scale_max=15
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
        Field(validation_alias="st_LoadPs/i_MaxLoad", ge=0, le=15),
        VariableMeta(
            name="max-ps-load",
            display_name="Checkstay PT Max Load",
            scale_min=0,
            scale_max=15,
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
        Field(validation_alias="st_LoadSb/i_Load", ge=0, le=15),
        VariableMeta(
            name="sb-load", display_name="Checkstay SB", scale_min=0, scale_max=15
        ),
    ]
    max_load_sb: Annotated[
        MaxLoad,
        Field(validation_alias="st_LoadSb/i_MaxLoad", ge=0, le=15),
        VariableMeta(
            name="max-sb-load",
            display_name="Checkstay SB Max Load",
            scale_min=0,
            scale_max=15,
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
        Field(ge=0, le=10),
        VariableMeta(display_name="Cunningham", scale_min=0, scale_max=10),
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
    load: Load
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad


class MainOuthaul(LoadsModel, ABC):
    TOPIC = "sail-systems/f0201-main-outhaul"
    load: Annotated[
        Load,
        Field(ge=0, le=25),
        VariableMeta(display_name="Outhaul", scale_min=0, scale_max=25),
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
        Field(ge=0, le=23),
        VariableMeta(display_name="Preventer", scale_min=0, scale_max=23),
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
        Field(ge=0, le=29),
        VariableMeta(
            display_name="Runner PT",
            scale_min=0,
            scale_max=29,
            side="port",
            applies_if="windward",
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
        Field(ge=0, le=29),
        VariableMeta(
            display_name="Runner SB",
            scale_min=0,
            scale_max=29,
            side="starboard",
            applies_if="windward",
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
        Field(ge=0, le=17),
        VariableMeta(display_name="Sheet", scale_min=0, scale_max=17),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad


class MainVang(LoadsModel, ABC):
    TOPIC = "sail-systems/f0202-main-vang"
    load: Annotated[
        Load,
        Field(ge=-32, le=67, validation_alias="i_Load"),
        VariableMeta(
            display_name="Vang",
            scale_min=-32,
            scale_max=67,
            scale_min_label="push",
            scale_max_label="pull",
        ),
    ]
    load_alarm: Annotated[
        LoadAlarm,
        Field(
            validation_alias="ox_LoadAlarm"
        ),  # TODO: check if this is proper alarm to take
    ]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(display_name="Vang", scale_min_label="out", scale_max_label="in"),
    ]
    max_position_alarm: MaxPositionAlarm
    min_position_alarm: MinPositionAlarm


class MainTraveller(LoadsModel, ABC):
    TOPIC = "sail-systems/fe405-main-sheet-traveller-winch"
    load: Load
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="Traveller",
            scale_min=-1,
            scale_max=1,
            scale_min_label="ps",
            scale_max_label="sb",
        ),
    ]
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
        Field(ge=0, le=1),
        VariableMeta(
            name="deflector-load", display_name="Deflector", scale_min=0, scale_max=1
        ),
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
        Field(validation_alias="st_Load/i_MaxLoadSetting", ge=0, le=8),
        VariableMeta(
            name="deflector-max-load",
            display_name="Deflector Max Load",
            scale_min=0,
            scale_max=8,
            threshold_for="load_alarm",
        ),
    ]

    load_ps: Annotated[
        Load,
        Field(validation_alias="st_LoadPs/i_Load", ge=0, le=2.7),
        VariableMeta(
            name="ps-load", display_name="Checkstay PT", scale_min=0, scale_max=2.7
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
        Field(validation_alias="st_LoadPs/i_MaxLoadSetting", ge=0, le=2.7),
        VariableMeta(
            name="max-ps-load",
            display_name="Checkstay PT Max Load",
            scale_min=0,
            scale_max=2.7,
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
        Field(validation_alias="st_LoadSb/i_Load", ge=0, le=2.7),
        VariableMeta(
            name="sb-load", display_name="Checkstay SB", scale_min=0, scale_max=2.7
        ),
    ]
    max_load_sb: Annotated[
        MaxLoad,
        Field(validation_alias="st_LoadSb/i_MaxLoadSetting", ge=0, le=2.7),
        VariableMeta(
            name="max-sb-load",
            display_name="Checkstay SB Max Load",
            scale_min=0,
            scale_max=2.7,
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
        Field(ge=0, le=6.7),
        VariableMeta(display_name="Cunningham", scale_min=0, scale_max=6.7),
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
        Field(ge=0, le=22),
        VariableMeta(display_name="Adjuster", scale_min=0, scale_max=22),
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
        Field(ge=0, le=17),
        VariableMeta(display_name="Outhaul", scale_min=0, scale_max=17),
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
        Field(ge=0, le=15.5),
        VariableMeta(display_name="Preventer", scale_min=0, scale_max=15.5),
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
        Field(ge=0, le=12.6),
        VariableMeta(
            display_name="Runner PT",
            scale_min=0,
            scale_max=12.6,
            side="port",
            applies_if="windward",
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
        Field(ge=0, le=12.6),
        VariableMeta(
            display_name="Runner SB",
            scale_min=0,
            scale_max=12.6,
            side="starboard",
            applies_if="windward",
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
        Field(ge=0, le=8.8),
        VariableMeta(display_name="Sheet", scale_min=0, scale_max=8.8),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad


class MizzenVang(LoadsModel, ABC):
    TOPIC = "sail-systems/f0502-mizzen-vang"
    load: Annotated[
        Load,
        Field(ge=-24.2, le=36.3, validation_alias="i_Load"),
        VariableMeta(
            display_name="Vang",
            scale_min=-24.2,
            scale_max=36.3,
            scale_min_label="push",
            scale_max_label="pull",
        ),
    ]
    load_alarm: Annotated[
        LoadAlarm,
        Field(
            validation_alias="ox_LoadAlarm"
        ),  # TODO: check if this is proper alarm to take
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
        Field(ge=0, le=16.5),
        VariableMeta(display_name="Sheet PT", scale_min=0, scale_max=16.5),
    ]
    load_failure: LoadFailure
    load_alarm: LoadAlarm
    max_load: MaxLoad


class StaysailSheetFeederSb(LoadsModel, ABC):
    TOPIC = "sail-systems/fe304-staysail-sheet-sb-feeder"
    load: Annotated[
        Load,
        Field(ge=0, le=16.5),
        VariableMeta(display_name="Sheet SB", scale_min=0, scale_max=16.5),
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
