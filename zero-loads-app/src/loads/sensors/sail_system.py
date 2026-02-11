from abc import ABC
from typing import Annotated

from pydantic import Field

from .base import LoadsModel
from .units import Alarm, Load, Lock, Position, RelativePosition, VariableMeta


class CaptiveWinch(LoadsModel, ABC):
    position: Annotated[Position, Field(validation_alias="ow_ActPos_mm")]
    relative_position: Annotated[
        RelativePosition, Field(validation_alias="ow_ActPos_pm")
    ]


class Cylinder(LoadsModel, ABC):
    load: Annotated[Load, Field(validation_alias="ow_ActLoad_10kg")]
    position: Annotated[Position, Field(validation_alias="ow_ActPos_mm")]
    relative_position: Annotated[
        RelativePosition, Field(validation_alias="relative_position_dummy")
    ]
    relief_load: Annotated[Load, Field(validation_alias="ow_RelfLoad_10kg")]
    alarm: Annotated[Alarm, Field(validation_alias="ox_LoadAlarm")]


class CylinderTwoPositions(LoadsModel, ABC):
    load: Annotated[Load, Field(validation_alias="ow_ActLoad_10kg")]
    position_1: Annotated[Position, Field(validation_alias="ow_ActPos_mm")]
    relative_position_1: Annotated[
        RelativePosition, Field(validation_alias="relative_position_dummy")
    ]
    position_2: Annotated[Position, Field(validation_alias="ow_ActPos2_mm")]
    relative_position_2: Annotated[
        RelativePosition, Field(validation_alias="relative_position_dummy")
    ]
    relief_load: Annotated[
        Load, Field(validation_alias="ow_RelfLoad_10kg"), VariableMeta(ignore=True)
    ]
    alarm: Annotated[
        Alarm, Field(validation_alias="ox_LoadAlarm"), VariableMeta(ignore=True)
    ]


class Deflector(LoadsModel, ABC):
    position: Annotated[
        Position,
        Field(validation_alias="ow_ActPos_mm"),
        VariableMeta(name="deflector-position"),
    ]
    relative_position: Annotated[
        RelativePosition,
        Field(validation_alias="relative_position_dummy"),
        VariableMeta(name="deflector-relative_position"),
    ]
    load: Annotated[
        Load,
        Field(validation_alias="i_ActualLoad_10kg"),
        VariableMeta(name="deflector-load"),
    ]
    relief_load: Annotated[
        Load, Field(validation_alias="i_RelfLoad_10kg"), VariableMeta(ignore=True)
    ]
    alarm: Annotated[
        Alarm, Field(validation_alias="ox_LoadAlarm"), VariableMeta(ignore=True)
    ]


class LoadCell(LoadsModel, ABC):
    load: Annotated[Load, Field(validation_alias="ow_ActLoad_10kg")]
    relief_load: Annotated[
        Load,
        Field(validation_alias="ow_RelfLoad_10kg"),
        VariableMeta(ignore=True),
    ]
    alarm: Annotated[
        Alarm, Field(validation_alias="ox_LoadAlarm"), VariableMeta(ignore=True)
    ]


class Vang(LoadsModel, ABC):
    load_bottom: Annotated[
        Load,
        Field(validation_alias="i_ActualLoadBottom"),
        VariableMeta(name="load_bottom"),
    ]
    load_rod: Annotated[
        Load, Field(validation_alias="i_ActualLoadRod"), VariableMeta(name="load_rod")
    ]
    position: Annotated[Position, Field(validation_alias="ow_ActPos_mm")]
    relative_position: Annotated[
        RelativePosition, Field(validation_alias="relative_position_dummy")
    ]


class Winch(LoadsModel, ABC):
    pass


class PrimaryWinchPs(LoadCell):
    TOPIC = "sail-systems/fe212_prmrywnchps"


class PrimaryWinchSb(LoadCell):
    TOPIC = "sail-systems/fe308_prmrywnchsb"


class MainWinchPsFwd(Winch):
    TOPIC = "sail-systems/fe209_mnwnchfwdps"


class MainWinchSbFwd(Winch):
    TOPIC = "sail-systems/fe305_mnwnchfwdsb"


class MainWinchPsAft(Winch):
    TOPIC = "sail-systems/fe210_mnwnchaftps"


class MainWinchSbAft(Winch):
    TOPIC = "sail-systems/fe306_mnwnchaftsb"


class MizzenWinchSb(Winch):
    TOPIC = "sail-systems/fe507_mzznwnchsb"


class MizzenWinchPs(Winch):
    TOPIC = "sail-systems/fe407_mzznwnchps"


class AftWinchPs(LoadCell):
    TOPIC = "sail-systems/fe408_aftwnchps"


class AftWinchSb(LoadCell):
    TOPIC = "sail-systems/fe508_aftwnchsb"


class BladeAdjuster(Cylinder):
    TOPIC = "sail-systems/f0103_bldadjstr"


class BladeCunningham(CylinderTwoPositions):
    TOPIC = "sail-systems/f0101_bldcnnnghm"


class BladeSheetCaptivePs(CaptiveWinch):
    TOPIC = "sail-systems/fe201_bldshtps"


class BladeSheetCaptiveSb(CaptiveWinch):
    TOPIC = "sail-systems/fe301_bldshtsb"


class BladeSheetFeederPs(LoadCell):
    TOPIC = "sail-systems/fe202_bldshtfdrps"


class BladeSheetFeederSb(LoadCell):
    TOPIC = "sail-systems/fe302_bldshtfdrsb"


class BladeTweakerPs(Cylinder):
    TOPIC = "sail-systems/f0206_bldtwkrps"


class BladeTweakerSb(Cylinder):
    TOPIC = "sail-systems/f0207_bldtwkrsb"


class CodeSailTack(CylinderTwoPositions):
    TOPIC = "sail-systems/f0102_cdtckcyl"


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
        Load, Field(validation_alias="i_ActualLoadPs"), VariableMeta(name="ps-load")
    ]
    load_sb: Annotated[
        Load,
        Field(validation_alias="i_ActualLoadSb"),
        VariableMeta(name="sb-load"),
    ]


class MainCunningham(Cylinder):
    TOPIC = "sail-systems/f0205_mncnnnghm"


class MainHalyard(CaptiveWinch, LoadCell):
    TOPIC = "sail-systems/fe207_mnhlyrd"
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


class MainOuthaul(Cylinder):
    TOPIC = "sail-systems/f0201_mnothl"


class MainPreventer(Cylinder):
    TOPIC = "sail-systems/f0204_mnbmprvntr"


class MainRunnerPs(CaptiveWinch, LoadCell):
    TOPIC = "sail-systems/fe401_mnrnnrps"


class MainRunnerSb(CaptiveWinch, LoadCell):
    TOPIC = "sail-systems/fe501_mnrnnrsb"


class MainSheet(CaptiveWinch, LoadCell):
    TOPIC = "sail-systems/fe205_mnsht"


class MainVang(Vang, LoadCell):
    TOPIC = "sail-systems/f0202_mnbmvng"


class MainTraveler(LoadsModel, ABC):
    TOPIC = "sail-systems/fe405_mntrvllr"
    position: Annotated[Position, Field(validation_alias="ow_ActPos_mm")]
    relative_position: Annotated[
        RelativePosition, Field(validation_alias="ow_ActPos_pm")
    ]


class MizzenCheckstay(Deflector):
    TOPIC = "sail-systems/f0503_mzznckstydflctr"
    load_ps: Annotated[
        Load, Field(validation_alias="i_ActualLoadPs"), VariableMeta(name="ps-load")
    ]
    load_sb: Annotated[
        Load, Field(validation_alias="i_ActualLoadSb"), VariableMeta(name="sb-load")
    ]


class MizzenCunningham(Cylinder):
    TOPIC = "sail-systems/f0504_mzzncnnnghm"


class MizzenHalyard(CaptiveWinch, LoadCell):
    TOPIC = "sail-systems/fe404_mzznhlyrd"
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
    lock_3: Annotated[
        Lock,
        Field(validation_alias="ox_IndctMzznHlyrdLck3_Ext"),
        VariableMeta(name="lock_3"),
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


class MizzenHeadsailTackAdjuster(Cylinder):
    TOPIC = "sail-systems/f0402_mzznhdsladjstr"


class MizzenOuthaul(Cylinder):
    TOPIC = "sail-systems/f0501_mzznothl"


class MizzenPreventer(Cylinder):
    TOPIC = "sail-systems/f0506_mzznbmprvntr"


class MizzenRunnerPs(CaptiveWinch, LoadCell):
    TOPIC = "sail-systems/fe402_mzznrnnrps"


class MizzenRunnerSb(CaptiveWinch, LoadCell):
    TOPIC = "sail-systems/fe502_mzznrnnrsb"


class MizzenSheet(CaptiveWinch, LoadCell):
    TOPIC = "sail-systems/fe504_mzznsht"


class MizzenVang(Vang, LoadCell):
    TOPIC = "sail-systems/f0502_mzznbmvng"


class StaysailSheetPs(CaptiveWinch):
    TOPIC = "sail-systems/fe203_styslshtps"


class StaysailSheetSb(CaptiveWinch):
    TOPIC = "sail-systems/fe303_styslshtsb"


class StaysailSheetFeederPs(LoadCell):
    TOPIC = "sail-systems/fe204_styslshtfdrps"


class StaysailSheetFeederSb(LoadCell):
    TOPIC = "sail-systems/fe304_styslshtfdrsb"


class StaysailStayAdjuster(Cylinder):
    TOPIC = "sail-systems/f0104_stysladjstr"
