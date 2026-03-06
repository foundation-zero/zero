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
    Field(validation_alias="ow_ActLoad_10kg"),
    BeforeValidator(decakilogram_to_tonne),
    ScalingMeta(
        conversion=decakilogram_to_tonne,
        inverse_conversion=tonne_to_decakilogram,
    ),
    VariableMeta(name="load"),
]
ConstrainedLoad: TypeAlias = Annotated[
    Load,
    Field(ge=0, le=20),
    VariableMeta(scale_min=0, scale_max=20),
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
    Field(validation_alias="relative_position_dummy"),
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
    TOPIC = "sail-systems/fe212_prmrywnchps"
    load: Annotated[
        Load,
        Field(validation_alias="ow_ActLoad_10kg"),
        Field(ge=0, le=15),
        VariableMeta(name="load", scale_min=0, scale_max=15),
    ]


class PrimaryWinchSb(LoadsModel, ABC):
    TOPIC = "sail-systems/fe308_prmrywnchsb"
    load: Annotated[
        Load,
        Field(validation_alias="ow_ActLoad_10kg"),
        Field(ge=0, le=15),
        VariableMeta(name="load", scale_min=0, scale_max=15),
    ]


class AftWinchPs(LoadsModel, ABC):
    TOPIC = "sail-systems/fe408_aftwnchps"
    load: Annotated[
        Load,
        Field(validation_alias="ow_ActLoad_10kg"),
        Field(ge=0, le=9),
        VariableMeta(name="load", scale_min=0, scale_max=9),
    ]


class AftWinchSb(LoadsModel, ABC):
    TOPIC = "sail-systems/fe508_aftwnchsb"
    load: Annotated[
        Load,
        Field(validation_alias="ow_ActLoad_10kg"),
        Field(ge=0, le=9),
        VariableMeta(name="load", scale_min=0, scale_max=9),
    ]


class BladeAdjuster(LoadsModel, ABC):
    TOPIC = "sail-systems/f0103_bldadjstr"
    load: Annotated[Load, VariableMeta(display_name="adjuster")]


class BladeCunningham(LoadsModel, ABC):
    TOPIC = "sail-systems/f0101_bldcnnnghm"
    load: Annotated[
        Load,
        VariableMeta(
            display_name="adjuster",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]


class BladeSheetFeederPs(LoadsModel, ABC):
    TOPIC = "sail-systems/fe202_bldshtfdrps"
    load: Annotated[
        Load,
        Field(ge=0, le=20),
        VariableMeta(display_name="sheet ps", scale_min=0, scale_max=20),
    ]


class BladeSheetFeederSb(LoadsModel, ABC):
    TOPIC = "sail-systems/fe302_bldshtfdrsb"
    load: Annotated[
        Load,
        Field(ge=0, le=20),
        VariableMeta(display_name="sheet sb", scale_min=0, scale_max=20),
    ]


class BladeTweakerPs(LoadsModel, ABC):
    TOPIC = "sail-systems/f0206_bldtwkrps"
    load: Annotated[ConstrainedLoad, VariableMeta(display_name="tweaker ps")]
    relative_position: Annotated[
        RelativePosition,
        Field(ge=0, le=15),
        VariableMeta(
            display_name="tweaker ps",
            scale_min_label="out",
            scale_max_label="in",
            scale_min=0,
            scale_max=15,
        ),
    ]


class BladeTweakerSb(LoadsModel, ABC):
    TOPIC = "sail-systems/f0207_bldtwkrsb"
    load: Annotated[ConstrainedLoad, VariableMeta(display_name="tweaker sb")]
    relative_position: Annotated[
        RelativePosition,
        Field(ge=0, le=15),
        VariableMeta(
            display_name="tweaker sb",
            scale_min_label="out",
            scale_max_label="in",
            scale_min=0,
            scale_max=15,
        ),
    ]


class CodeZeroTack(LoadsModel, ABC):
    TOPIC = "sail-systems/f0102_cdtckcyl"
    load: Annotated[
        Load,
        Field(ge=0, le=33),
        VariableMeta(display_name="tack", scale_min=0, scale_max=33),
    ]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(display_name="tack", scale_min_label="out", scale_max_label="in"),
    ]


class A2Tack(LoadsModel, ABC):
    TOPIC = "sail-systems/a2-tack-placeholder"
    load: Annotated[ConstrainedLoad, VariableMeta(display_name="tack")]


class StormJibTack(LoadsModel, ABC):
    TOPIC = "sail-systems/storm-jib-tack-placeholder"
    load: Annotated[
        Load,
        Field(ge=0, le=30),
        VariableMeta(display_name="tack", scale_min=0, scale_max=30),
    ]


class MainHeadstayCombined(LoadsModel, ABC):
    TOPIC = "sail-systems/combined-headstay-placeholder"
    load: Annotated[
        Load,
        Field(ge=0, le=66),
        VariableMeta(display_name="headstay combined", scale_min=0, scale_max=66),
    ]


class HeadsailLocks(LoadsModel, ABC):
    TOPIC = "sail-systems/mnmst"
    lock_A2: Annotated[
        Lock,
        Field(validation_alias="ox_IndctA2Lck_Ext"),
        VariableMeta(name="lock_a2", type="actual"),
    ]
    overhoist_A2: Annotated[
        Lock,
        Field(validation_alias="ox_IndctA2LckOvrhst_Ext"),
        VariableMeta(name="overhoist_a2", type="actual"),
    ]
    lock_A3C0: Annotated[
        Lock,
        Field(validation_alias="ox_IndctA3C0Lck_Ext"),
        VariableMeta(name="lock_a3c0", type="actual"),
    ]
    overhoist_A3C0: Annotated[
        Lock,
        Field(validation_alias="ox_IndctA3C0LckOverhst_Ext"),
        VariableMeta(name="overhoist_a3c0", type="actual"),
    ]
    lock_staysail: Annotated[
        Lock,
        Field(validation_alias="ox_IndctStyslLck_Ext"),
        VariableMeta(name="lock_staysail", type="actual"),
    ]
    overhoist_staysail: Annotated[
        Lock,
        Field(validation_alias="ox_IndctStyslLckOverhst_Ext"),
        VariableMeta(name="overhoist_staysail", type="actual"),
    ]
    lock_stormjib: Annotated[
        Lock,
        Field(validation_alias="ox_IndctStmjbLck_Ext"),
        VariableMeta(name="lock_stormjib", type="actual"),
    ]
    overhoist_stormjib: Annotated[
        Lock,
        Field(validation_alias="ox_IndctStmjbLckOvrhst_Ext"),
        VariableMeta(name="overhoist_stormjib", type="actual"),
    ]


class MainCheckstay(LoadsModel, ABC):
    TOPIC = "sail-systems/f0203_mnchckstydflctr"
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            name="deflector-relative-position",
            display_name="deflector",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]
    load: Annotated[
        Load,
        Field(ge=0, le=8),
        VariableMeta(
            name="deflector-load", display_name="deflector", scale_min=0, scale_max=8
        ),
    ]
    relief_load: ReliefLoad
    alarm: Annotated[Alarm, VariableMeta(alarm_for="deflector-load")]
    load_ps: Annotated[
        Load,
        Field(validation_alias="i_ActualLoadPs", ge=0, le=15),
        VariableMeta(
            name="ps-load", display_name="checkstay ps", scale_min=0, scale_max=15
        ),
    ]
    load_sb: Annotated[
        Load,
        Field(validation_alias="i_ActualLoadSb", ge=0, le=15),
        VariableMeta(
            name="sb-load", display_name="checkstay sb", scale_min=0, scale_max=15
        ),
    ]


class MainCunningham(LoadsModel, ABC):
    TOPIC = "sail-systems/f0205_mncnnnghm"
    load: Annotated[
        Load,
        Field(ge=0, le=10),
        VariableMeta(display_name="cunningham", scale_min=0, scale_max=10),
    ]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="cunningham",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]


class MainHalyard(LoadsModel, ABC):
    TOPIC = "sail-systems/fe207_mnhlyrd"
    load: ConstrainedLoad
    lock_full: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHlyrdLckFh_Ext"),
        VariableMeta(name="lock_full", type="actual"),
    ]
    lock_1: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHlyrdLck1_Ext"),
        VariableMeta(name="lock_1", type="actual"),
    ]
    lock_2: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHlyrdLck2_Ext"),
        VariableMeta(name="lock_2", type="actual"),
    ]
    lock_3: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHlyrdLck3_Ext"),
        VariableMeta(name="lock_3", type="actual"),
    ]
    overhoist_full: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHlyrdLckFhOvrhst_Ext"),
        VariableMeta(name="overhoist_full", type="actual"),
    ]
    overhoist_1: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHlyrdLck1Ovrhst_Ext"),
        VariableMeta(name="overhoist_1", type="actual"),
    ]
    overhoist_2: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHlyrdLck2Ovrhst_Ext"),
        VariableMeta(name="overhoist_2", type="actual"),
    ]
    overhoist_3: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHlyrdLck3Ovrhst_Ext"),
        VariableMeta(name="overhoist_3", type="actual"),
    ]
    boom_lock_1: Annotated[
        Lock,
        Field(validation_alias="ox_IndctBmRfLck1_Ext"),
        VariableMeta(name="boom_lock_1", type="actual"),
    ]
    boom_lock_2: Annotated[
        Lock,
        Field(validation_alias="ox_IndctBmRfLck2_Ext"),
        VariableMeta(name="boom_lock_2", type="actual"),
    ]
    boom_lock_3: Annotated[
        Lock,
        Field(validation_alias="ox_IndctBmRfLck3_Ext"),
        VariableMeta(name="boom_lock_3", type="actual"),
    ]


class MainOuthaul(LoadsModel, ABC):
    TOPIC = "sail-systems/f0201_mnothl"
    load: Annotated[
        Load,
        Field(ge=0, le=25),
        VariableMeta(display_name="outhaul", scale_min=0, scale_max=25),
    ]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="outhaul", scale_min_label="out", scale_max_label="in"
        ),
    ]


class MainPreventer(LoadsModel, ABC):
    TOPIC = "sail-systems/f0204_mnbmprvntr"
    load: Annotated[
        Load,
        Field(ge=0, le=23),
        VariableMeta(display_name="preventer", scale_min=0, scale_max=23),
    ]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="preventer",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]


class MainRunnerPs(LoadsModel, ABC):
    TOPIC = "sail-systems/fe401_mnrnnrps"
    load: Annotated[
        Load,
        Field(ge=0, le=29),
        VariableMeta(display_name="runner ps", scale_min=0, scale_max=29),
    ]


class MainRunnerSb(LoadsModel, ABC):
    TOPIC = "sail-systems/fe501_mnrnnrsb"
    load: Annotated[
        Load,
        Field(ge=0, le=29),
        VariableMeta(display_name="runner sb", scale_min=0, scale_max=29),
    ]


class MainSheet(LoadsModel, ABC):
    TOPIC = "sail-systems/fe205_mnsht"
    load: Annotated[
        Load,
        Field(ge=0, le=17),
        VariableMeta(display_name="sheet", scale_min=0, scale_max=17),
    ]


class MainVang(LoadsModel, ABC):
    TOPIC = "sail-systems/f0202_mnbmvng"
    load: Annotated[
        Load,
        Field(ge=-32, le=67),
        VariableMeta(
            display_name="vang",
            scale_min=-32,
            scale_max=67,
            scale_min_label="push",
            scale_max_label="pull",
        ),
    ]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(display_name="vang", scale_min_label="out", scale_max_label="in"),
    ]


class MainTraveller(LoadsModel, ABC):
    TOPIC = "sail-systems/fe405_mntrvllr"
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="traveller",
            scale_min=-1,
            scale_max=1,
            scale_min_label="ps",
            scale_max_label="sb",
        ),
    ]


class MizzenCheckstay(LoadsModel, ABC):
    TOPIC = "sail-systems/f0503_mzznckstydflctr"
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            name="deflector-relative-position",
            display_name="deflector",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]
    load: Annotated[
        Load,
        Field(ge=0, le=1),
        VariableMeta(
            name="deflector-load", display_name="deflector", scale_min=0, scale_max=1
        ),
    ]
    relief_load: ReliefLoad
    alarm: Annotated[Alarm, VariableMeta(alarm_for="deflector-load")]
    load_ps: Annotated[
        Load,
        Field(validation_alias="i_ActualLoadPs", ge=0, le=2.7),
        VariableMeta(
            name="ps-load", display_name="checkstay ps", scale_min=0, scale_max=2.7
        ),
    ]
    load_sb: Annotated[
        Load,
        Field(validation_alias="i_ActualLoadSb", ge=0, le=2.7),
        VariableMeta(
            name="sb-load", display_name="checkstay sb", scale_min=0, scale_max=2.7
        ),
    ]


class MizzenCunningham(LoadsModel, ABC):
    TOPIC = "sail-systems/f0504_mzzncnnnghm"
    load: Annotated[
        Load,
        Field(ge=0, le=6.7),
        VariableMeta(display_name="cunningham", scale_min=0, scale_max=6.7),
    ]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="cunningham", scale_min_label="out", scale_max_label="in"
        ),
    ]


class MizzenHalyard(LoadsModel, ABC):
    TOPIC = "sail-systems/fe404_mzznhlyrd"
    load: ConstrainedLoad
    lock_full: Annotated[
        Lock,
        Field(validation_alias="ox_IndctMzznHlyrdLckFh_Ext"),
        VariableMeta(name="lock_full", type="actual"),
    ]
    lock_1: Annotated[
        Lock,
        Field(validation_alias="ox_IndctMzznHlyrdLck1_Ext"),
        VariableMeta(name="lock_1", type="actual"),
    ]
    lock_2: Annotated[
        Lock,
        Field(validation_alias="ox_IndctMzznHlyrdLck2_Ext"),
        VariableMeta(name="lock_2", type="actual"),
    ]
    overhoist_full: Annotated[
        Lock,
        Field(validation_alias="ox_IndctMzznHlyrdLckFhOvrhst_Ext"),
        VariableMeta(name="overhoist_full", type="actual"),
    ]
    overhoist_1: Annotated[
        Lock,
        Field(validation_alias="ox_IndctMzznHlyrdLck1Ovrhst_Ext"),
        VariableMeta(name="overhoist_1", type="actual"),
    ]
    overhoist_2: Annotated[
        Lock,
        Field(validation_alias="ox_IndctMzznHlyrdLck2Ovrhst_Ext"),
        VariableMeta(name="overhoist_2", type="actual"),
    ]
    boom_lock_1: Annotated[
        Lock,
        Field(validation_alias="ox_IndctMzznBmRfLck1_Ext"),
        VariableMeta(name="boom_lock_1", type="actual"),
    ]
    boom_lock_2: Annotated[
        Lock,
        Field(validation_alias="ox_IndctMzznBmRfLck2_Ext"),
        VariableMeta(name="boom_lock_2", type="actual"),
    ]


class MizzenHeadsailLocks(LoadsModel, ABC):
    TOPIC = "sail-systems/f0401_mzznhdfrlr"
    lock: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHdslLck_Ext"),
        VariableMeta(name="lock", type="actual"),
    ]
    overhoist: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHdslLckOvrhst_Ext"),
        VariableMeta(name="overhoist", type="actual"),
    ]


class MizzenHeadsailTackAdjuster(LoadsModel, ABC):
    TOPIC = "sail-systems/f0402_mzznhdsladjstr"
    load: Annotated[
        Load,
        Field(ge=0, le=22),
        VariableMeta(display_name="adjuster", type="actual", scale_min=0, scale_max=22),
    ]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="adjuster",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]


class MizzenOuthaul(LoadsModel, ABC):
    TOPIC = "sail-systems/f0501_mzznothl"
    load: Annotated[
        Load,
        Field(ge=0, le=17),
        VariableMeta(display_name="outhaul", scale_min=0, scale_max=17),
    ]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="outhaul", scale_min_label="out", scale_max_label="in"
        ),
    ]


class MizzenPreventer(LoadsModel, ABC):
    TOPIC = "sail-systems/f0506_mzznbmprvntr"
    load: Annotated[
        Load,
        Field(ge=0, le=15.5),
        VariableMeta(display_name="preventer", scale_min=0, scale_max=15.5),
    ]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="preventer",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]


class MizzenRunnerPs(LoadsModel, ABC):
    TOPIC = "sail-systems/fe402_mzznrnnrps"
    load: Annotated[
        Load,
        Field(ge=0, le=12.6),
        VariableMeta(display_name="runner ps", scale_min=0, scale_max=12.6),
    ]


class MizzenRunnerSb(LoadsModel, ABC):
    TOPIC = "sail-systems/fe502_mzznrnnrsb"
    load: Annotated[
        Load,
        Field(ge=0, le=12.6),
        VariableMeta(display_name="runner sb", scale_min=0, scale_max=12.6),
    ]


class MizzenSheet(LoadsModel, ABC):
    TOPIC = "sail-systems/fe504_mzznsht"
    load: Annotated[
        Load,
        Field(ge=0, le=8.8),
        VariableMeta(display_name="sheet", scale_min=0, scale_max=8.8),
    ]


class MizzenVang(LoadsModel, ABC):
    TOPIC = "sail-systems/f0502_mzznbmvng"
    load: Annotated[
        Load,
        Field(ge=-24.2, le=36.3),
        VariableMeta(
            display_name="vang",
            scale_min=-24.2,
            scale_max=36.3,
            scale_min_label="push",
            scale_max_label="pull",
        ),
    ]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(display_name="vang", scale_min_label="out", scale_max_label="in"),
    ]


class StaysailSheetFeederPs(LoadsModel, ABC):
    TOPIC = "sail-systems/fe204_styslshtfdrps"
    load: Annotated[
        Load,
        Field(ge=0, le=16.5),
        VariableMeta(display_name="sheet ps", scale_min=0, scale_max=16.5),
    ]


class StaysailSheetFeederSb(LoadsModel, ABC):
    TOPIC = "sail-systems/fe304_styslshtfdrsb"
    load: Annotated[
        Load,
        Field(ge=0, le=16.5),
        VariableMeta(display_name="sheet sb", scale_min=0, scale_max=16.5),
    ]


class StaysailStayAdjuster(LoadsModel, ABC):
    TOPIC = "sail-systems/f0104_stysladjstr"
    load: Annotated[
        Load,
        VariableMeta(display_name="adjuster", type="actual"),
    ]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="adjuster",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]
