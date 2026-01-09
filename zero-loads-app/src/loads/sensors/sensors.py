from abc import ABC

from pydantic import Field

from .base import LoadsModel
from .units import (
    DeciKilogram,
    Millimeter,
    Promille,
)


class CaptiveWinch(LoadsModel, ABC):
    load: DeciKilogram = Field(validation_alias="ow_ActLoad_10kg")
    position: Millimeter = Field(validation_alias="ow_ActPos_mm")
    relative_position: Promille = Field(validation_alias="ow_ActPos_pm")
    relief_load: DeciKilogram = Field(validation_alias="ow_RelfLoad_10kg")


class Cylinder(LoadsModel, ABC):
    load: DeciKilogram = Field(validation_alias="ow_ActLoad_10kg")
    position: Millimeter = Field(validation_alias="ow_ActPos_mm")
    relief_load: DeciKilogram = Field(validation_alias="ow_RelfLoad_10kg")


class CylinderTwoPositions(LoadsModel, ABC):
    load: DeciKilogram = Field(validation_alias="ow_ActLoad_10kg")
    position_1: Millimeter = Field(validation_alias="ow_ActPos_mm")
    position_2: Millimeter = Field(validation_alias="ow_ActPos2_mm")
    relief_load: DeciKilogram = Field(validation_alias="ow_RelfLoad_10kg")


class Deflector(LoadsModel, ABC):
    position: Millimeter = Field(validation_alias="ow_ActPos_mm")
    load: DeciKilogram = Field(validation_alias="i_ActualLoad_10kg")
    load_ps: DeciKilogram = Field(validation_alias="i_ActualLoadPs")  # correct here?
    load_sb: DeciKilogram = Field(validation_alias="i_ActualLoadSb")
    relief_load: DeciKilogram = Field(validation_alias="i_RelfLoad_10kg")


class LoadCell(LoadsModel, ABC):
    load: DeciKilogram = Field(validation_alias="ow_ActLoad_10kg")
    relief_load: DeciKilogram = Field(validation_alias="ow_RelfLoad_10kg")


class Vang(LoadsModel, ABC):
    load_bottom: DeciKilogram = Field(validation_alias="ow_ActLoad_10kg")
    load_rod: DeciKilogram = Field(validation_alias="ow_ActLoad2_10kg")
    position: Millimeter = Field(validation_alias="ow_ActPos_mm")
    relief_load: DeciKilogram = Field(validation_alias="ow_RelfLoad_10kg")


class BladeAdjuster(Cylinder):
    TOPIC = "sail-systems/f0103_bldadjstr"


class BladeCunningham(CylinderTwoPositions):
    TOPIC = "sail-systems/f0101_bldcnnnghm"


class BladeSheetCaptivePS(CaptiveWinch):
    TOPIC = "sail-systems/fe201_bldshtps"


class BladeSheetCaptiveSB(CaptiveWinch):
    TOPIC = "sail-systems/fe301_bldshtsb"


class BladeSheetFeederPs(LoadCell):
    TOPIC = "sail-systems/fe202_bldshtfdrps"


class BladeSheetFeederSb(LoadCell):
    TOPIC = "sail-systems/fe302_bldshtfdrsb"


class BladeTweakerPS(Cylinder):
    TOPIC = "sail-systems/f0206_bldtwkrps"


class BladeTweakerSB(Cylinder):
    TOPIC = "sail-systems/f0207_bldtwkrsb"


class CodeSailTack(CylinderTwoPositions):
    TOPIC = "sail-systems/f0102_cdtckcyl"


class HeadsailLocks(LoadsModel, ABC):
    TOPIC = "sail-systems/MnMst"
    A2_lock: bool = Field(validation_alias="ox_IndctA2Lck_Ext")
    A2_overhoist: bool = Field(validation_alias="ox_IndctA2LckOvrhst_Ext")
    A3C0_lock: bool = Field(validation_alias="ox_IndctA3C0Lck_Ext")
    A3C0_overhoist: bool = Field(validation_alias="ox_IndctA3C0LckOverhst_Ext")
    staysail_lock: bool = Field(validation_alias="ox_IndctStyslLck_Ext")
    staysail_overhoist: bool = Field(validation_alias="ox_IndctStyslLckOverhst_Ext")
    stormjib_lock: bool = Field(validation_alias="ox_IndctStmjbLck_Ext")
    stormjib_overhoist: bool = Field(validation_alias="ox_IndctStmjbLckOvrhst_Ext")


class MainCheckstayDeflector(Deflector):
    TOPIC = "sail-systems/f0203_mnchckstydflctr"


class MainCunningham(Cylinder):
    TOPIC = "sail-systems/f0205_mncnnnghm"


class MainHalyard(CaptiveWinch):
    TOPIC = "sail-systems/fe207_mnhlyrd"
    lock_full: bool = Field(validation_alias="ox_IndctHlyrdLckFh_Ext")
    lock_1: bool = Field(validation_alias="ox_IndctHlyrdLck1_Ext")
    lock_2: bool = Field(validation_alias="ox_IndctHlyrdLck2_Ext")
    lock_3: bool = Field(validation_alias="ox_IndctHlyrdLck3_Ext")
    overhoist_full: bool = Field(validation_alias="ox_IndctHlyrdLckFhOvrhst_Ext")
    overhoist_1: bool = Field(validation_alias="ox_IndctHlyrdLck1Ovrhst_Ext")
    overhoist_2: bool = Field(validation_alias="ox_IndctHlyrdLck2Ovrhst_Ext")
    overhoist_3: bool = Field(validation_alias="ox_IndctHlyrdLck3Ovrhst_Ext")
    boom_lock_1: bool = Field(validation_alias="ox_IndctBmRfLck1_Ext")
    boom_lock_2: bool = Field(validation_alias="ox_IndctBmRfLck2_Ext")
    boom_lock_3: bool = Field(validation_alias="ox_IndctBmRfLck3_Ext")


class MainOuthaul(Cylinder):
    TOPIC = "sail-systems/f0201_mnothl"


class MainPreventer(Cylinder):
    TOPIC = "sail-systems/f0204_mnbmprvntr"


class MainRunnerCaptivePS(CaptiveWinch):
    TOPIC = "sail-systems/fe401_mnrnnrps"


class MainRunnerCaptiveSB(CaptiveWinch):
    TOPIC = "sail-systems/fe501_mnrnnrsb"


class MainSheetCaptive(CaptiveWinch):
    TOPIC = "sail-systems/fe205_mnsht"


class MainVang(Vang):
    TOPIC = "sail-systems/f0202_mnbmvng"


class MizzenCheckstayDeflector(Deflector):
    TOPIC = "sail-systems/f0503_mzznckstydflctr"


class MizzenCunningham(Cylinder):
    TOPIC = "sail-systems/f0504_mzzncnnnghm"


class MizzenHalyard(CaptiveWinch):
    TOPIC = "sail-systems/fe404_mzznhlyrd"
    lock_full: bool = Field(validation_alias="ox_IndctMzznHlyrdLckFh_Ext")
    lock_1: bool = Field(validation_alias="ox_IndctMzznHlyrdLck1_Ext")
    lock_2: bool = Field(validation_alias="ox_IndctMzznHlyrdLck2_Ext")
    lock_3: bool = Field(validation_alias="ox_IndctMzznHlyrdLck3_Ext")
    overhoist_full: bool = Field(validation_alias="ox_IndctMzznHlyrdLckFhOvrhst_Ext")
    overhoist_1: bool = Field(validation_alias="ox_IndctMzznHlyrdLck1Ovrhst_Ext")
    overhoist_2: bool = Field(validation_alias="ox_IndctMzznHlyrdLck2Ovrhst_Ext")
    overhoist_3: bool = Field(validation_alias="ox_IndctMzznHlyrdLck3Ovrhst_Ext")
    boom_lock_1: bool = Field(validation_alias="ox_IndctMzznBmRfLck1_Ext")
    boom_lock_2: bool = Field(validation_alias="ox_IndctMzznBmRfLck2_Ext")


class MizzenHeadsailLocks(LoadsModel, ABC):
    TOPIC = "sail-systems/f0401_mzznhdfrlr"
    lock: bool = Field(validation_alias="ox_IndctHdslLck_Ext")
    overhoist: bool = Field(validation_alias="ox_IndctHdslLckOvrhst_Ext")


class MizzenHeadsailTackAdjuster(Cylinder):
    TOPIC = "sail-systems/f0402_mzznhdsladjstr"


class MizzenOuthaul(Cylinder):
    TOPIC = "sail-systems/f0501_mzznothl"
    # loadBm?


class MizzenPreventer(Cylinder):
    TOPIC = "sail-systems/f0506_mzznbmprvntr"


class MizzenRunnerCaptivePS(CaptiveWinch):
    TOPIC = "sail-systems/fe402_mzznrnnrps"


class MizzenRunnerCaptiveSB(CaptiveWinch):
    TOPIC = "sail-systems/fe502_mzznrnnrsb"


class MizzenSheetCaptive(CaptiveWinch):
    TOPIC = "sail-systems/fe504_mzznsht"


class MizzenVang(Vang):
    TOPIC = "sail-systems/f0502_mzznbmvng"


class StaysailSheetCaptivePS(CaptiveWinch):
    TOPIC = "sail-systems/fe203_styslshtps"


class StaysailSheetCaptiveSB(CaptiveWinch):
    TOPIC = "sail-systems/fe303_styslshtsb"


class StaysailSheetFeederPs(LoadCell):
    TOPIC = "sail-systems/fe204_styslshtfdrps"


class StaysailSheetFeederSb(LoadCell):
    TOPIC = "sail-systems/fe304_styslshtfdrsb"


class StaysailStayAdjuster(Cylinder):
    TOPIC = "sail-systems/f0104_stysladjstr"
