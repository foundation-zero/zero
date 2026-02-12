from abc import ABC
from typing import Annotated

from pydantic import Field

from .base import LoadsModel
from .units import (
    Alarm,
    Load,
    LoadBase,
    Lock,
    RelativePosition,
    ReliefLoad,
    VariableMeta,
)


class Adjuster(LoadsModel, ABC):
    load: Annotated[Load, VariableMeta(display_name="adjuster", type="actual")]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="adjuster",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]


class Cunningham(LoadsModel, ABC):
    load: Annotated[Load, VariableMeta(display_name="cunningham")]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="cunningham",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]


class Deflector(LoadsModel, ABC):
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
        VariableMeta(name="deflector-load", display_name="deflector"),
    ]
    relief_load: ReliefLoad
    alarm: Annotated[Alarm, VariableMeta(alarm_for="deflector-load")]


class Feeder(LoadsModel, ABC):
    load: Annotated[Load, VariableMeta(display_name="sheet")]


class Outhaul(LoadsModel, ABC):
    load: Annotated[Load, VariableMeta(display_name="outhaul")]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="outhaul", scale_min_label="out", scale_max_label="in"
        ),
    ]


class Preventer(LoadsModel, ABC):
    load: Annotated[Load, VariableMeta(display_name="preventer")]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="preventer",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]


class Vang(LoadsModel, ABC):
    load: Annotated[
        LoadBase,
        Field(ge=-10, le=10),
        VariableMeta(
            display_name="vang",
            scale_min=-10,
            scale_max=10,
            scale_min_label="push",
            scale_max_label="pull",
        ),
    ]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(display_name="vang", scale_min_label="out", scale_max_label="in"),
    ]


class PrimaryWinchPs(LoadsModel, ABC):
    TOPIC = "sail-systems/fe212_prmrywnchps"
    load: Load


class PrimaryWinchSb(LoadsModel, ABC):
    TOPIC = "sail-systems/fe308_prmrywnchsb"
    load: Load


class AftWinchPs(LoadsModel, ABC):
    TOPIC = "sail-systems/fe408_aftwnchps"
    load: Load


class AftWinchSb(LoadsModel, ABC):
    TOPIC = "sail-systems/fe508_aftwnchsb"
    load: Load


class BladeAdjuster(Adjuster):
    TOPIC = "sail-systems/f0103_bldadjstr"


class BladeCunningham(Cunningham):
    TOPIC = "sail-systems/f0101_bldcnnnghm"


class BladeSheetFeederPs(Feeder):
    TOPIC = "sail-systems/fe202_bldshtfdrps"


class BladeSheetFeederSb(Feeder):
    TOPIC = "sail-systems/fe302_bldshtfdrsb"


class BladeTweakerPs(LoadsModel, ABC):
    TOPIC = "sail-systems/f0206_bldtwkrps"
    load: Annotated[Load, VariableMeta(display_name="tweaker ps")]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="tweaker ps",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]


class BladeTweakerSb(LoadsModel, ABC):
    TOPIC = "sail-systems/f0207_bldtwkrsb"
    load: Annotated[Load, VariableMeta(display_name="tweaker sb")]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            display_name="tweaker sb",
            scale_min_label="out",
            scale_max_label="in",
        ),
    ]


class CodeZeroTack(LoadsModel, ABC):
    TOPIC = "sail-systems/f0102_cdtckcyl"
    load: Annotated[Load, VariableMeta(display_name="tack")]
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(display_name="tack", scale_min_label="out", scale_max_label="in"),
    ]


class A2Tack(LoadsModel, ABC):
    TOPIC = "sail-systems/a2-tack-placeholder"
    load: Annotated[Load, VariableMeta(display_name="tack")]


class StormJibTack(LoadsModel, ABC):
    TOPIC = "sail-systems/storm-jib-tack-placeholder"
    load: Annotated[Load, VariableMeta(display_name="tack")]


class CombinedHeadstay(LoadsModel, ABC):
    TOPIC = "sail-systems/combined-headstay-placeholder"
    load: Annotated[Load, VariableMeta(display_name="combined headstay")]


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


class MainCheckstay(Deflector):
    TOPIC = "sail-systems/f0203_mnchckstydflctr"
    load_ps: Annotated[
        Load,
        Field(validation_alias="i_ActualLoadPs"),
        VariableMeta(name="ps-load", display_name="checkstay ps"),
    ]
    load_sb: Annotated[
        Load,
        Field(validation_alias="i_ActualLoadSb"),
        VariableMeta(name="sb-load", display_name="checkstay sb"),
    ]


class MainCunningham(Cunningham):
    TOPIC = "sail-systems/f0205_mncnnnghm"


class MainHalyard(LoadsModel, ABC):
    TOPIC = "sail-systems/fe207_mnhlyrd"
    load: Load
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


class MainOuthaul(Outhaul):
    TOPIC = "sail-systems/f0201_mnothl"


class MainPreventer(Preventer):
    TOPIC = "sail-systems/f0204_mnbmprvntr"


class MainRunnerPs(LoadsModel, ABC):
    TOPIC = "sail-systems/fe401_mnrnnrps"
    load: Annotated[Load, VariableMeta(display_name="runner ps")]


class MainRunnerSb(LoadsModel, ABC):
    TOPIC = "sail-systems/fe501_mnrnnrsb"
    load: Annotated[Load, VariableMeta(display_name="runner sb")]


class MainSheet(LoadsModel, ABC):
    TOPIC = "sail-systems/fe205_mnsht"
    load: Annotated[Load, VariableMeta(display_name="sheet")]


class MainVang(Vang, ABC):
    TOPIC = "sail-systems/f0202_mnbmvng"


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


class MizzenCheckstay(Deflector):
    TOPIC = "sail-systems/f0503_mzznckstydflctr"
    load_ps: Annotated[Load, VariableMeta(name="ps-load", display_name="checkstay ps")]
    load_sb: Annotated[Load, VariableMeta(name="sb-load", display_name="checkstay sb")]


class MizzenCunningham(LoadsModel, ABC):
    TOPIC = "sail-systems/f0504_mzzncnnnghm"
    load: Annotated[Load, VariableMeta(display_name="cunningham")]
    relative_position: Annotated[
        RelativePosition, VariableMeta(display_name="cunningham")
    ]


class MizzenHalyard(LoadsModel, ABC):
    TOPIC = "sail-systems/fe404_mzznhlyrd"
    load: Load
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


class MizzenHeadsailTackAdjuster(Adjuster):
    TOPIC = "sail-systems/f0402_mzznhdsladjstr"


class MizzenOuthaul(Outhaul):
    TOPIC = "sail-systems/f0501_mzznothl"


class MizzenPreventer(Preventer):
    TOPIC = "sail-systems/f0506_mzznbmprvntr"


class MizzenRunnerPs(LoadsModel, ABC):
    TOPIC = "sail-systems/fe402_mzznrnnrps"
    load: Annotated[Load, VariableMeta(display_name="runner ps")]


class MizzenRunnerSb(LoadsModel, ABC):
    TOPIC = "sail-systems/fe502_mzznrnnrsb"
    load: Annotated[Load, VariableMeta(display_name="runner sb")]


class MizzenSheet(LoadsModel, ABC):
    TOPIC = "sail-systems/fe504_mzznsht"
    load: Annotated[Load, VariableMeta(display_name="sheet")]


class MizzenVang(Vang):
    TOPIC = "sail-systems/f0502_mzznbmvng"


class StaysailSheetFeederPs(Feeder, ABC):
    TOPIC = "sail-systems/fe204_styslshtfdrps"


class StaysailSheetFeederSb(Feeder, ABC):
    TOPIC = "sail-systems/fe304_styslshtfdrsb"


class StaysailStayAdjuster(Adjuster):
    TOPIC = "sail-systems/f0104_stysladjstr"
