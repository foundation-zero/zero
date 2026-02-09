from abc import ABC
from typing import Annotated

from pydantic import Field

from .base import LoadsModel
from .units import (
    Alarm,
    Load,
    Lock,
    RelativePosition,
    ReliefLoad,
    VariableMeta,
)


class Adjuster(LoadsModel, ABC):
    load: Annotated[Load, VariableMeta(display_name="Adjuster Load")]
    relative_position: Annotated[
        RelativePosition, VariableMeta(display_name="Adjuster Position")
    ]
    relief_load: Annotated[
        ReliefLoad, VariableMeta(display_name="Adjuster Relief Load")
    ]


class Cunningham(LoadsModel, ABC):
    load: Annotated[Load, VariableMeta(display_name="Cunningham Load")]
    relative_position: Annotated[
        RelativePosition, VariableMeta(display_name="Cunningham Position")
    ]


class Deflector(LoadsModel, ABC):
    relative_position: Annotated[
        RelativePosition,
        VariableMeta(
            name="deflector-relative_position",
            display_name="Deflector Position",
        ),
    ]
    load: Annotated[
        Load,
        VariableMeta(name="deflector-load", display_name="Deflector Load"),
    ]
    relief_load: ReliefLoad
    alarm: Alarm


class Feeder(LoadsModel, ABC):
    load: Annotated[Load, VariableMeta(display_name="Sheet Load")]


class Outhaul(LoadsModel, ABC):
    load: Annotated[Load, VariableMeta(display_name="Outhaul Load")]
    relative_position: Annotated[
        RelativePosition, VariableMeta(display_name="Outhaul Position")
    ]


class Preventer(LoadsModel, ABC):
    load: Annotated[Load, VariableMeta(display_name="Preventer Load")]
    relative_position: Annotated[
        RelativePosition, VariableMeta(display_name="Preventer Position")
    ]


class Tweaker(LoadsModel, ABC):
    load: Annotated[Load, VariableMeta(display_name="Tweaker Load")]
    relative_position: Annotated[
        RelativePosition, VariableMeta(display_name="Tweaker Relative Position")
    ]
    relief_load: Annotated[ReliefLoad, VariableMeta(display_name="Tweaker Relief Load")]


class Vang(LoadsModel, ABC):
    load: Annotated[Load, VariableMeta(display_name="Vang Load")]
    relative_position: Annotated[
        RelativePosition, VariableMeta(display_name="Vang Position")
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


class BladeTweakerPs(Tweaker):
    TOPIC = "sail-systems/f0206_bldtwkrps"


class BladeTweakerSb(Tweaker):
    TOPIC = "sail-systems/f0207_bldtwkrsb"


class CodeZeroTack(LoadsModel, ABC):
    TOPIC = "sail-systems/f0102_cdtckcyl"
    load: Annotated[Load, VariableMeta(display_name="Tack Load")]
    relative_position: Annotated[
        RelativePosition, VariableMeta(display_name="Tack Position")
    ]


class HeadsailLocks(LoadsModel, ABC):
    TOPIC = "sail-systems/mnmst"
    lock_A2: Annotated[
        Lock, Field(validation_alias="ox_IndctA2Lck_Ext"), VariableMeta(name="lock_a2")
    ]
    overhoist_A2: Annotated[
        Lock,
        Field(validation_alias="ox_IndctA2LckOvrhst_Ext"),
        VariableMeta(name="overhoist_a2"),
    ]
    lock_A3C0: Annotated[
        Lock,
        Field(validation_alias="ox_IndctA3C0Lck_Ext"),
        VariableMeta(name="lock_a3c0"),
    ]
    overhoist_A3C0: Annotated[
        Lock,
        Field(validation_alias="ox_IndctA3C0LckOverhst_Ext"),
        VariableMeta(name="overhoist_a3c0"),
    ]
    lock_staysail: Annotated[
        Lock,
        Field(validation_alias="ox_IndctStyslLck_Ext"),
        VariableMeta(name="lock_staysail"),
    ]
    overhoist_staysail: Annotated[
        Lock,
        Field(validation_alias="ox_IndctStyslLckOverhst_Ext"),
        VariableMeta(name="overhoist_staysail"),
    ]
    lock_stormjib: Annotated[
        Lock,
        Field(validation_alias="ox_IndctStmjbLck_Ext"),
        VariableMeta(name="lock_stormjib"),
    ]
    overhoist_stormjib: Annotated[
        Lock,
        Field(validation_alias="ox_IndctStmjbLckOvrhst_Ext"),
        VariableMeta(name="overhoist_stormjib"),
    ]


class MainCheckstay(Deflector):
    TOPIC = "sail-systems/f0203_mnchckstydflctr"
    load_ps: Annotated[
        Load, Field(validation_alias="i_ActualLoadPs"), VariableMeta(name="ps-load", display_name="Checkstay Ps Load")
    ]
    load_sb: Annotated[
        Load,
        Field(validation_alias="i_ActualLoadSb"),
        VariableMeta(name="sb-load"),
    ]


class MainCunningham(Cunningham):
    TOPIC = "sail-systems/f0205_mncnnnghm"


class MainHalyard(LoadsModel, ABC):
    TOPIC = "sail-systems/fe207_mnhlyrd"
    load: Load
    lock_full: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHlyrdLckFh_Ext"),
        VariableMeta(name="lock_full"),
    ]
    lock_1: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHlyrdLck1_Ext"),
        VariableMeta(name="lock_1"),
    ]
    lock_2: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHlyrdLck2_Ext"),
        VariableMeta(name="lock_2"),
    ]
    lock_3: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHlyrdLck3_Ext"),
        VariableMeta(name="lock_3"),
    ]
    overhoist_full: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHlyrdLckFhOvrhst_Ext"),
        VariableMeta(name="overhoist_full"),
    ]
    overhoist_1: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHlyrdLck1Ovrhst_Ext"),
        VariableMeta(name="overhoist_1"),
    ]
    overhoist_2: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHlyrdLck2Ovrhst_Ext"),
        VariableMeta(name="overhoist_2"),
    ]
    overhoist_3: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHlyrdLck3Ovrhst_Ext"),
        VariableMeta(name="overhoist_3"),
    ]
    boom_lock_1: Annotated[
        Lock,
        Field(validation_alias="ox_IndctBmRfLck1_Ext"),
        VariableMeta(name="boom_lock_1"),
    ]
    boom_lock_2: Annotated[
        Lock,
        Field(validation_alias="ox_IndctBmRfLck2_Ext"),
        VariableMeta(name="boom_lock_2"),
    ]
    boom_lock_3: Annotated[
        Lock,
        Field(validation_alias="ox_IndctBmRfLck3_Ext"),
        VariableMeta(name="boom_lock_3"),
    ]


class MainOuthaul(Outhaul):
    TOPIC = "sail-systems/f0201_mnothl"


class MainPreventer(Preventer):
    TOPIC = "sail-systems/f0204_mnbmprvntr"


class MainRunnerPs(LoadsModel, ABC):
    TOPIC = "sail-systems/fe401_mnrnnrps"
    load: Annotated[Load, VariableMeta(display_name="Runner Ps Load")]


class MainRunnerSb(LoadsModel, ABC):
    TOPIC = "sail-systems/fe501_mnrnnrsb"
    load: Annotated[Load, VariableMeta(display_name="Runner Sb Load")]


class MainSheet(LoadsModel, ABC):
    TOPIC = "sail-systems/fe205_mnsht"
    load: Annotated[Load, VariableMeta(display_name="Sheet Load")]


class MainVang(Vang, ABC):
    TOPIC = "sail-systems/f0202_mnbmvng"


class MainTraveler(LoadsModel, ABC):
    TOPIC = "sail-systems/fe405_mntrvllr"
    load: Annotated[Load, VariableMeta(display_name="Traveler Load")]
    relative_position: Annotated[
        RelativePosition, VariableMeta(display_name="Traveler Position")
    ]


class MizzenCheckstay(Deflector):
    TOPIC = "sail-systems/f0503_mzznckstydflctr"
    load_ps: Annotated[Load, VariableMeta(name="ps-load", display_name="Ps Load")]
    load_sb: Annotated[Load, VariableMeta(name="sb-load", display_name="Sb Load")]


class MizzenCunningham(LoadsModel, ABC):
    TOPIC = "sail-systems/f0504_mzzncnnnghm"
    load: Annotated[Load, VariableMeta(display_name="Cunningham Load")]
    relative_position: Annotated[
        RelativePosition, VariableMeta(display_name="Cunningham Position")
    ]


class MizzenHalyard(LoadsModel, ABC):
    TOPIC = "sail-systems/fe404_mzznhlyrd"
    load: Load
    lock_full: Annotated[
        Lock,
        Field(validation_alias="ox_IndctMzznHlyrdLckFh_Ext"),
        VariableMeta(name="lock_full"),
    ]
    lock_1: Annotated[
        Lock,
        Field(validation_alias="ox_IndctMzznHlyrdLck1_Ext"),
        VariableMeta(name="lock_1"),
    ]
    lock_2: Annotated[
        Lock,
        Field(validation_alias="ox_IndctMzznHlyrdLck2_Ext"),
        VariableMeta(name="lock_2"),
    ]
    overhoist_full: Annotated[
        Lock,
        Field(validation_alias="ox_IndctMzznHlyrdLckFhOvrhst_Ext"),
        VariableMeta(name="overhoist_full"),
    ]
    overhoist_1: Annotated[
        Lock,
        Field(validation_alias="ox_IndctMzznHlyrdLck1Ovrhst_Ext"),
        VariableMeta(name="overhoist_1"),
    ]
    overhoist_2: Annotated[
        Lock,
        Field(validation_alias="ox_IndctMzznHlyrdLck2Ovrhst_Ext"),
        VariableMeta(name="overhoist_2"),
    ]
    boom_lock_1: Annotated[
        Lock,
        Field(validation_alias="ox_IndctMzznBmRfLck1_Ext"),
        VariableMeta(name="boom_lock_1"),
    ]
    boom_lock_2: Annotated[
        Lock,
        Field(validation_alias="ox_IndctMzznBmRfLck2_Ext"),
        VariableMeta(name="boom_lock_2"),
    ]


class MizzenHeadsailLocks(LoadsModel, ABC):
    TOPIC = "sail-systems/f0401_mzznhdfrlr"
    lock: Annotated[
        Lock, Field(validation_alias="ox_IndctHdslLck_Ext"), VariableMeta(name="lock")
    ]
    overhoist: Annotated[
        Lock,
        Field(validation_alias="ox_IndctHdslLckOvrhst_Ext"),
        VariableMeta(name="overhoist"),
    ]


class MizzenHeadsailTackAdjuster(Adjuster):
    TOPIC = "sail-systems/f0402_mzznhdsladjstr"


class MizzenOuthaul(Outhaul):
    TOPIC = "sail-systems/f0501_mzznothl"


class MizzenPreventer(Preventer):
    TOPIC = "sail-systems/f0506_mzznbmprvntr"


class MizzenRunnerPs(LoadsModel, ABC):
    TOPIC = "sail-systems/fe402_mzznrnnrps"
    load: Annotated[Load, VariableMeta(display_name="Runner Ps Load")]


class MizzenRunnerSb(LoadsModel, ABC):
    TOPIC = "sail-systems/fe502_mzznrnnrsb"
    load: Annotated[Load, VariableMeta(display_name="Runner Sb Load")]


class MizzenSheet(LoadsModel, ABC):
    TOPIC = "sail-systems/fe504_mzznsht"
    load: Annotated[Load, VariableMeta(display_name="Sheet Load")]


class MizzenVang(Vang):
    TOPIC = "sail-systems/f0502_mzznbmvng"


class StaysailSheetFeederPs(Feeder, ABC):
    TOPIC = "sail-systems/fe204_styslshtfdrps"


class StaysailSheetFeederSb(Feeder, ABC):
    TOPIC = "sail-systems/fe304_styslshtfdrsb"


class StaysailStayAdjuster(Adjuster):
    TOPIC = "sail-systems/f0104_stysladjstr"
