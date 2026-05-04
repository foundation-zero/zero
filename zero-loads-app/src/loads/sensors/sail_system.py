from abc import ABC
from typing import Annotated, TypeAlias

from pydantic import AliasPath, BeforeValidator, Field

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
    Position as BasePosition,
)
from .units import (
    RelativePosition as BaseRelativePosition,
)
from .units import (
    ReliefLoad as BaseReliefLoad,
)

Load: TypeAlias = Annotated[  # Needed to be able to override Field constraints where needed (e.g. in Vang). Pydantic has no fixed order to resolve nested `Field`s in inside of `Annotated`s
    BaseLoad,
    Field(validation_alias="i_ActualLoad"),
    BeforeValidator(decakilogram_to_tonne),
    ScalingMeta(
        conversion=decakilogram_to_tonne,
        inverse_conversion=tonne_to_decakilogram,
    ),
    VariableMeta(name="load"),
]

ReliefLoad: TypeAlias = Annotated[
    BaseReliefLoad,
    Field(ge=0, le=20, validation_alias="ow_RelfLoad_10kg"),
    BeforeValidator(decakilogram_to_tonne),
    ScalingMeta(
        conversion=decakilogram_to_tonne,
        inverse_conversion=tonne_to_decakilogram,
    ),
]
RelativePosition: TypeAlias = Annotated[
    BaseRelativePosition,
    Field(validation_alias=AliasPath("st_position", "i_Position_permille")),
    VariableMeta(name="relative-position"),
    BeforeValidator(per_mille_to_ratio),
    ScalingMeta(
        conversion=per_mille_to_ratio,
        inverse_conversion=ratio_to_per_mille,
    ),
]
Position: TypeAlias = Annotated[
    BasePosition,
    Field(validation_alias="ow_ActPos_mm"),
    VariableMeta(scale_min=0, scale_max=100),
]

Alarm: TypeAlias = Annotated[
    BaseAlarm,
    Field(validation_alias="ox_LoadAlarm"),
    VariableMeta(unit="bool", name="alarm", type="alarm"),
]


class PrimaryWinchPs(LoadsModel, ABC):
    TOPIC = "sail-systems/fe212-primary-deck-winch-ps"
    load: Annotated[
        Load,
        Field(validation_alias=AliasPath("st_load", "i_Load")),
        Field(ge=0, le=15),
        VariableMeta(display_name="Primary PS", scale_min=0, scale_max=15),
    ]


class PrimaryWinchSb(LoadsModel, ABC):
    TOPIC = "sail-systems/fe308-primary-deck-winch-sb"
    load: Annotated[
        Load,
        Field(validation_alias=AliasPath("st_load", "i_Load")),
        Field(ge=0, le=15),
        VariableMeta(display_name="Primary SB", scale_min=0, scale_max=15),
    ]


class AftWinchPs(LoadsModel, ABC):
    TOPIC = "sail-systems/fe408-aft-deck-deck-winch-ps"
    load: Annotated[
        Load,
        Field(validation_alias=AliasPath("st_load", "i_Load")),
        Field(ge=0, le=9),
        VariableMeta(display_name="Aft Winch PS", scale_min=0, scale_max=9),
    ]


class AftWinchSb(LoadsModel, ABC):
    TOPIC = "sail-systems/fe508-aft-deck-deck-winch-sb"
    load: Annotated[
        Load,
        Field(validation_alias=AliasPath("st_load", "i_Load")),
        Field(ge=0, le=9),
        VariableMeta(display_name="Aft Winch SB", scale_min=0, scale_max=9),
    ]


class BladeAdjuster(LoadsModel, ABC):
    TOPIC = "sail-systems/f0103-blade-adjuster"
    load: Annotated[Load, VariableMeta(display_name="Adjuster")]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="Adjuster",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]


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
    relative_position: Annotated[
        RelativePosition,
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
        VariableMeta(display_name="Sheet PS", scale_min=0, scale_max=20),
    ]


class BladeSheetFeederSb(LoadsModel, ABC):
    TOPIC = "sail-systems/fe302-blade-sheet-sb-feeder"
    load: Annotated[
        Load,
        Field(ge=0, le=20),
        VariableMeta(display_name="Sheet SB", scale_min=0, scale_max=20),
    ]


class BladeTweakerPs(LoadsModel, ABC):
    TOPIC = "sail-systems/f0206-blade-tweaker-ps"
    load: Annotated[
        Load,
        Field(ge=0, le=15),
        VariableMeta(display_name="Tweaker PS", scale_min=0, scale_max=15),
    ]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="Tweaker PS",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]


class BladeTweakerSb(LoadsModel, ABC):
    TOPIC = "sail-systems/f0207-blade-tweaker-sb"
    load: Annotated[
        Load,
        Field(ge=0, le=15),
        VariableMeta(display_name="Tweaker SB", scale_min=0, scale_max=15),
    ]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="Tweaker SB",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]


class CodeZeroTack(LoadsModel, ABC):
    TOPIC = "sail-systems/f0102-code-sail-tack"
    load: Annotated[
        Load,
        Field(ge=0, le=33),
        VariableMeta(display_name="Tack", scale_min=0, scale_max=33),
    ]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(display_name="Tack", scale_min_label="out", scale_max_label="in"),
    ]


class A2Tack(LoadsModel, ABC):
    TOPIC = "sail-systems/a2-tack-placeholder"
    load: Annotated[Load, VariableMeta(display_name="Tack")]


class StormJibTack(LoadsModel, ABC):
    TOPIC = "sail-systems/storm-jib-tack-placeholder"
    load: Annotated[
        Load,
        Field(ge=0, le=30),
        VariableMeta(display_name="Tack", scale_min=0, scale_max=30),
    ]


class MainHeadstayCombined(LoadsModel, ABC):
    TOPIC = "sail-systems/combined-headstay-placeholder"
    load: Annotated[
        Load,
        Field(ge=0, le=66),
        VariableMeta(display_name="Headstay Combined", scale_min=0, scale_max=66),
    ]


class HeadsailLocks(LoadsModel, ABC):
    TOPIC = "sail-systems/mast"  # TODO: double-check — aliases (ox_IndctA2Lck_Ext, ox_IndctStyslLck_Ext, ox_IndctStmjbLck_Ext, …) suggest this could be fe207-main-halyard-captive-winch or a dedicated headsail topic
    lock_A2: Annotated[
        Lock,
        Field(validation_alias="ox_IndctA2Lck_Ext"),
        VariableMeta(name="lock_a2", display_name="A2"),
    ]
    overhoist_A2: Annotated[
        Lock,
        Field(validation_alias="ox_IndctA2LckOvrhst_Ext"),
        VariableMeta(name="overhoist_a2", display_name="A2"),
    ]
    lock_A3C0: Annotated[
        Lock,
        Field(validation_alias="ox_IndctA3C0Lck_Ext"),
        VariableMeta(name="lock_a3c0", display_name="A3/C0"),
    ]
    overhoist_A3C0: Annotated[
        Lock,
        Field(validation_alias="ox_IndctA3C0LckOverhst_Ext"),
        VariableMeta(name="overhoist_a3c0", display_name="A3/C0"),
    ]
    lock_staysail: Annotated[
        Lock,
        Field(validation_alias="ox_IndctStyslLck_Ext"),
        VariableMeta(name="lock_staysail", display_name="Staysail"),
    ]
    overhoist_staysail: Annotated[
        Lock,
        Field(validation_alias="ox_IndctStyslLckOverhst_Ext"),
        VariableMeta(name="overhoist_staysail", display_name="Staysail"),
    ]
    lock_stormjib: Annotated[
        Lock,
        Field(validation_alias="ox_IndctStmjbLck_Ext"),
        VariableMeta(name="lock_stormjib", display_name="Storm Jib"),
    ]
    overhoist_stormjib: Annotated[
        Lock,
        Field(validation_alias="ox_IndctStmjbLckOvrhst_Ext"),
        VariableMeta(name="overhoist_stormjib", display_name="Storm Jib"),
    ]


class MainCheckstay(LoadsModel, ABC):
    TOPIC = "sail-systems/f0203-main-checkstay-deflector"
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            name="deflector-relative-position",
            display_name="Deflector",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]
    load: Annotated[
        Load,
        Field(ge=0, le=8),
        VariableMeta(
            name="deflector-load", display_name="Deflector", scale_min=0, scale_max=8
        ),
    ]
    relief_load: ReliefLoad
    alarm: Annotated[Alarm, VariableMeta(alarm_for="deflector-load")]
    load_ps: Annotated[
        Load,
        Field(validation_alias="i_ActualLoadPs", ge=0, le=15),
        VariableMeta(
            name="ps-load", display_name="Checkstay PS", scale_min=0, scale_max=15
        ),
    ]
    load_sb: Annotated[
        Load,
        Field(validation_alias="i_ActualLoadSb", ge=0, le=15),
        VariableMeta(
            name="sb-load", display_name="Checkstay SB", scale_min=0, scale_max=15
        ),
    ]


class MainCunningham(LoadsModel, ABC):
    TOPIC = "sail-systems/f0205-main-cunningham"
    load: Annotated[
        Load,
        Field(ge=0, le=10),
        VariableMeta(display_name="Cunningham", scale_min=0, scale_max=10),
    ]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="Cunningham",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]


class MainHalyard(LoadsModel, ABC):
    TOPIC = "sail-systems/fe207-main-halyard-captive-winch"
    load: Load
    lock_full: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHlyrdLckFh_Ext"),
        VariableMeta(name="lock_full", display_name="Masthead"),
    ]
    lock_1: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHlyrdLck1_Ext"),
        VariableMeta(name="lock_1", display_name="Reef 1"),
    ]
    lock_2: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHlyrdLck2_Ext"),
        VariableMeta(name="lock_2", display_name="Reef 2"),
    ]
    lock_3: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHlyrdLck3_Ext"),
        VariableMeta(name="lock_3", display_name="Reef 3"),
    ]
    overhoist_full: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHlyrdLckFhOvrhst_Ext"),
        VariableMeta(name="overhoist_full", display_name="Masthead"),
    ]
    overhoist_1: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHlyrdLck1Ovrhst_Ext"),
        VariableMeta(name="overhoist_1", display_name="Reef 1"),
    ]
    overhoist_2: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHlyrdLck2Ovrhst_Ext"),
        VariableMeta(name="overhoist_2", display_name="Reef 2"),
    ]
    overhoist_3: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHlyrdLck3Ovrhst_Ext"),
        VariableMeta(name="overhoist_3", display_name="Reef 3"),
    ]
    boom_lock_1: Annotated[
        Lock,
        Field(validation_alias="ox_IndctBmRfLck1_Ext"),
        VariableMeta(name="boom_lock_1", display_name="Boom 1"),
    ]
    boom_lock_2: Annotated[
        Lock,
        Field(validation_alias="ox_IndctBmRfLck2_Ext"),
        VariableMeta(name="boom_lock_2", display_name="Boom 2"),
    ]
    boom_lock_3: Annotated[
        Lock,
        Field(validation_alias="ox_IndctBmRfLck3_Ext"),
        VariableMeta(name="boom_lock_3", display_name="Boom 3"),
    ]


class MainOuthaul(LoadsModel, ABC):
    TOPIC = "sail-systems/f0201-main-outhaul"
    load: Annotated[
        Load,
        Field(ge=0, le=25),
        VariableMeta(display_name="Outhaul", scale_min=0, scale_max=25),
    ]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="Outhaul", scale_min_label="out", scale_max_label="in"
        ),
    ]


class MainPreventer(LoadsModel, ABC):
    TOPIC = "sail-systems/f0204-main-boom-preventer"
    load: Annotated[
        Load,
        Field(ge=0, le=23),
        VariableMeta(display_name="Preventer", scale_min=0, scale_max=23),
    ]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="Preventer",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]


class MainRunnerPs(LoadsModel, ABC):
    TOPIC = "sail-systems/fe401-main-runner-captive-winch-ps"
    load: Annotated[
        Load,
        Field(validation_alias=AliasPath("st_Load", "i_Load")),
        Field(ge=0, le=29),
        VariableMeta(display_name="Runner PS", scale_min=0, scale_max=29),
    ]


class MainRunnerSb(LoadsModel, ABC):
    TOPIC = "sail-systems/fe501-main-runner-captive-winch-sb"
    load: Annotated[
        Load,
        Field(validation_alias=AliasPath("st_Load", "i_Load")),
        Field(ge=0, le=29),
        VariableMeta(display_name="Runner SB", scale_min=0, scale_max=29),
    ]


class MainSheet(LoadsModel, ABC):
    TOPIC = "sail-systems/fe205-main-sheet-captive-winch"
    load: Annotated[
        Load,
        Field(validation_alias=AliasPath("st_Load", "i_Load")),
        Field(ge=0, le=17),
        VariableMeta(display_name="Sheet", scale_min=0, scale_max=17),
    ]


class MainVang(LoadsModel, ABC):
    TOPIC = "sail-systems/f0202-main-vang"
    load: Annotated[
        Load,
        Field(ge=-32, le=67),
        VariableMeta(
            display_name="Vang",
            scale_min=-32,
            scale_max=67,
            scale_min_label="push",
            scale_max_label="pull",
        ),
    ]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(display_name="Vang", scale_min_label="out", scale_max_label="in"),
    ]


class MainTraveller(LoadsModel, ABC):
    TOPIC = "sail-systems/fe405-main-sheet-traveller-winch"
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


class MizzenCheckstay(LoadsModel, ABC):
    TOPIC = "sail-systems/f0503-mizzen-checkstay-deflector"
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            name="deflector-relative-position",
            display_name="Deflector",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]
    load: Annotated[
        Load,
        Field(ge=0, le=1),
        VariableMeta(
            name="deflector-load", display_name="Deflector", scale_min=0, scale_max=1
        ),
    ]
    relief_load: ReliefLoad
    alarm: Annotated[Alarm, VariableMeta(alarm_for="deflector-load")]
    load_ps: Annotated[
        Load,
        Field(validation_alias="i_ActualLoadPs", ge=0, le=2.7),
        VariableMeta(
            name="ps-load", display_name="Checkstay PS", scale_min=0, scale_max=2.7
        ),
    ]
    load_sb: Annotated[
        Load,
        Field(validation_alias="i_ActualLoadSb", ge=0, le=2.7),
        VariableMeta(
            name="sb-load", display_name="Checkstay SB", scale_min=0, scale_max=2.7
        ),
    ]


class MizzenCunningham(LoadsModel, ABC):
    TOPIC = "sail-systems/f0504-mizzen-cunningham"
    load: Annotated[
        Load,
        Field(ge=0, le=6.7),
        VariableMeta(display_name="Cunningham", scale_min=0, scale_max=6.7),
    ]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="Cunningham", scale_min_label="out", scale_max_label="in"
        ),
    ]


class MizzenHalyard(LoadsModel, ABC):
    TOPIC = "sail-systems/fe404-mizzen-halyard-captive-winch"
    load: Annotated[Load, VariableMeta(display_name="Halyard")]
    lock_full: Annotated[
        Lock,
        Field(validation_alias="ox_IndctMzznHlyrdLckFh_Ext"),
        VariableMeta(name="lock_full", display_name="Masthead"),
    ]
    lock_1: Annotated[
        Lock,
        Field(validation_alias="ox_IndctMzznHlyrdLck1_Ext"),
        VariableMeta(name="lock_1", display_name="Reef 1"),
    ]
    lock_2: Annotated[
        Lock,
        Field(validation_alias="ox_IndctMzznHlyrdLck2_Ext"),
        VariableMeta(name="lock_2", display_name="Reef 2"),
    ]
    overhoist_full: Annotated[
        Lock,
        Field(validation_alias="ox_IndctMzznHlyrdLckFhOvrhst_Ext"),
        VariableMeta(name="overhoist_full", display_name="Masthead"),
    ]
    overhoist_1: Annotated[
        Lock,
        Field(validation_alias="ox_IndctMzznHlyrdLck1Ovrhst_Ext"),
        VariableMeta(name="overhoist_1", display_name="Reef 1"),
    ]
    overhoist_2: Annotated[
        Lock,
        Field(validation_alias="ox_IndctMzznHlyrdLck2Ovrhst_Ext"),
        VariableMeta(name="overhoist_2", display_name="Reef 2"),
    ]
    boom_lock_1: Annotated[
        Lock,
        Field(validation_alias="ox_IndctMzznBmRfLck1_Ext"),
        VariableMeta(name="boom_lock_1", display_name="Boom 1"),
    ]
    boom_lock_2: Annotated[
        Lock,
        Field(validation_alias="ox_IndctMzznBmRfLck2_Ext"),
        VariableMeta(name="boom_lock_2", display_name="Boom 2"),
    ]


class MizzenHeadsailLocks(LoadsModel, ABC):
    TOPIC = "sail-systems/f0401-mizzen-headsail-furler"  # TODO: double-check — aliases (ox_IndctHdslLck_Ext, ox_IndctHdslLckOvrhst_Ext) are lock indicators; furler topic may or may not carry these
    lock: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHdslLck_Ext"),
        VariableMeta(name="lock", display_name="Headsail"),
    ]
    overhoist: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHdslLckOvrhst_Ext"),
        VariableMeta(name="overhoist", display_name="Headsail"),
    ]


class MizzenHeadsailTackAdjuster(LoadsModel, ABC):
    TOPIC = "sail-systems/f0402-mizzen-headsail-tack-adjuster"
    load: Annotated[
        Load,
        Field(ge=0, le=22),
        VariableMeta(display_name="Adjuster", scale_min=0, scale_max=22),
    ]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="Adjuster",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]


class MizzenOuthaul(LoadsModel, ABC):
    TOPIC = "sail-systems/f0501-mizzen-outhaul"
    load: Annotated[
        Load,
        Field(ge=0, le=17),
        VariableMeta(display_name="Outhaul", scale_min=0, scale_max=17),
    ]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="Outhaul", scale_min_label="out", scale_max_label="in"
        ),
    ]


class MizzenPreventer(LoadsModel, ABC):
    TOPIC = "sail-systems/f0506-mizzen-boom-preventer"
    load: Annotated[
        Load,
        Field(ge=0, le=15.5),
        VariableMeta(display_name="Preventer", scale_min=0, scale_max=15.5),
    ]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="Preventer",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]


class MizzenRunnerPs(LoadsModel, ABC):
    TOPIC = "sail-systems/fe402-mizzen-runner-captive-winch-ps"
    load: Annotated[
        Load,
        Field(validation_alias=AliasPath("st_Load", "i_Load")),
        Field(ge=0, le=12.6),
        VariableMeta(display_name="Runner PS", scale_min=0, scale_max=12.6),
    ]


class MizzenRunnerSb(LoadsModel, ABC):
    TOPIC = "sail-systems/fe502-mizzen-runner-captive-winch-sb"
    load: Annotated[
        Load,
        Field(validation_alias=AliasPath("st_Load", "i_Load")),
        Field(ge=0, le=12.6),
        VariableMeta(display_name="Runner SB", scale_min=0, scale_max=12.6),
    ]


class MizzenSheet(LoadsModel, ABC):
    TOPIC = "sail-systems/fe504-mizzen-sheet-captive-winch"
    load: Annotated[
        Load,
        Field(validation_alias=AliasPath("st_Load", "i_Load")),
        Field(ge=0, le=8.8),
        VariableMeta(display_name="Sheet", scale_min=0, scale_max=8.8),
    ]


class MizzenVang(LoadsModel, ABC):
    TOPIC = "sail-systems/f0502-mizzen-vang"
    load: Annotated[
        Load,
        Field(ge=-24.2, le=36.3),
        VariableMeta(
            display_name="Vang",
            scale_min=-24.2,
            scale_max=36.3,
            scale_min_label="push",
            scale_max_label="pull",
        ),
    ]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(display_name="Vang", scale_min_label="out", scale_max_label="in"),
    ]


class StaysailSheetFeederPs(LoadsModel, ABC):
    TOPIC = "sail-systems/fe204-staysail-sheet-ps-feeder"
    load: Annotated[
        Load,
        Field(ge=0, le=16.5),
        VariableMeta(display_name="Sheet PS", scale_min=0, scale_max=16.5),
    ]


class StaysailSheetFeederSb(LoadsModel, ABC):
    TOPIC = "sail-systems/fe304-staysail-sheet-sb-feeder"
    load: Annotated[
        Load,
        Field(ge=0, le=16.5),
        VariableMeta(display_name="Sheet SB", scale_min=0, scale_max=16.5),
    ]


class StaysailStayAdjuster(LoadsModel, ABC):
    TOPIC = "sail-systems/f0104-staysail-stay-adjuster"
    load: Annotated[
        Load,
        VariableMeta(display_name="Adjuster"),
    ]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="Adjuster",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]
