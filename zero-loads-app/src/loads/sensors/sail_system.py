from abc import ABC

from pydantic import Field

from .base import LoadsModel
from .units import Alarm, Load, Lock, Position, RelativePosition


class CaptiveWinch(LoadsModel, ABC):
    position: Position = Field(validation_alias="ow_ActPos_mm")
    relative_position: RelativePosition = Field(validation_alias="ow_ActPos_pm")


class Cylinder(LoadsModel, ABC):
    load: Load = Field(validation_alias="ow_ActLoad_10kg")
    position: Position = Field(validation_alias="ow_ActPos_mm")
    relative_position: RelativePosition = Field(
        validation_alias="relative_position_dummy"
    )
    relief_load: Load = Field(validation_alias="ow_RelfLoad_10kg")
    alarm: Alarm = Field(validation_alias="ox_LoadAlarm")


class CylinderTwoPositions(LoadsModel, ABC):
    load: Load = Field(validation_alias="ow_ActLoad_10kg")
    position_1: Position = Field(validation_alias="ow_ActPos_mm")
    relative_position_1: RelativePosition = Field(
        validation_alias="relative_position_dummy"
    )
    position_2: Position = Field(validation_alias="ow_ActPos2_mm")
    relative_position_2: RelativePosition = Field(
        validation_alias="relative_position_dummy"
    )
    relief_load: Load = Field(validation_alias="ow_RelfLoad_10kg")
    alarm: Alarm = Field(validation_alias="ox_LoadAlarm")


class Deflector(LoadsModel, ABC):
    position: Position = Field(validation_alias="ow_ActPos_mm")
    relative_position: RelativePosition = Field(
        validation_alias="relative_position_dummy"
    )
    load_deflector: Load = Field(validation_alias="i_ActualLoad_10kg")
    load_ps: Load = Field(validation_alias="i_ActualLoadPs")
    load_sb: Load = Field(validation_alias="i_ActualLoadSb")
    relief_load: Load = Field(validation_alias="i_RelfLoad_10kg")
    alarm: Alarm = Field(validation_alias="ox_LoadAlarm")


class LoadCell(LoadsModel, ABC):
    load: Load = Field(validation_alias="ow_ActLoad_10kg")
    relief_load: Load = Field(validation_alias="ow_RelfLoad_10kg")
    alarm: Alarm = Field(validation_alias="ox_LoadAlarm")


class Vang(LoadsModel, ABC):
    load_bottom: Load = Field(validation_alias="i_ActualLoadBottom")
    load_rod: Load = Field(validation_alias="i_ActualLoadRod")
    position: Position = Field(validation_alias="ow_ActPos_mm")
    relative_position: RelativePosition = Field(
        validation_alias="relative_position_dummy"
    )


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
    TOPIC = "sail-systems/mnmst"
    lock_A2: Lock = Field(validation_alias="ox_IndctA2Lck_Ext")
    overhoist_A2: Lock = Field(validation_alias="ox_IndctA2LckOvrhst_Ext")
    lock_A3C0: Lock = Field(validation_alias="ox_IndctA3C0Lck_Ext")
    overhoist_A3C0: Lock = Field(validation_alias="ox_IndctA3C0LckOverhst_Ext")
    lock_staysail: Lock = Field(validation_alias="ox_IndctStyslLck_Ext")
    overhoist_staysail: Lock = Field(validation_alias="ox_IndctStyslLckOverhst_Ext")
    lock_stormjib: Lock = Field(validation_alias="ox_IndctStmjbLck_Ext")
    overhoist_stormjib: Lock = Field(validation_alias="ox_IndctStmjbLckOvrhst_Ext")


class MainCheckstayDeflector(Deflector):
    TOPIC = "sail-systems/f0203_mnchckstydflctr"


class MainCunningham(Cylinder):
    TOPIC = "sail-systems/f0205_mncnnnghm"


class MainHalyard(CaptiveWinch, LoadCell):
    TOPIC = "sail-systems/fe207_mnhlyrd"
    lock_full: Lock = Field(validation_alias="ox_IndctHlyrdLckFh_Ext")
    lock_1: Lock = Field(validation_alias="ox_IndctHlyrdLck1_Ext")
    lock_2: Lock = Field(validation_alias="ox_IndctHlyrdLck2_Ext")
    lock_3: Lock = Field(validation_alias="ox_IndctHlyrdLck3_Ext")
    overhoist_full: Lock = Field(validation_alias="ox_IndctHlyrdLckFhOvrhst_Ext")
    overhoist_1: Lock = Field(validation_alias="ox_IndctHlyrdLck1Ovrhst_Ext")
    overhoist_2: Lock = Field(validation_alias="ox_IndctHlyrdLck2Ovrhst_Ext")
    overhoist_3: Lock = Field(validation_alias="ox_IndctHlyrdLck3Ovrhst_Ext")
    boom_lock_1: Lock = Field(validation_alias="ox_IndctBmRfLck1_Ext")
    boom_lock_2: Lock = Field(validation_alias="ox_IndctBmRfLck2_Ext")
    boom_lock_3: Lock = Field(validation_alias="ox_IndctBmRfLck3_Ext")


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
    position: Position = Field(validation_alias="ow_ActPos_mm")
    relative_position: RelativePosition = Field(validation_alias="ow_ActPos_pm")


class MizzenCheckstayDeflector(Deflector):
    TOPIC = "sail-systems/f0503_mzznckstydflctr"


class MizzenCunningham(Cylinder):
    TOPIC = "sail-systems/f0504_mzzncnnnghm"


class MizzenHalyard(CaptiveWinch, LoadCell):
    TOPIC = "sail-systems/fe404_mzznhlyrd"
    lock_full: Lock = Field(validation_alias="ox_IndctMzznHlyrdLckFh_Ext")
    lock_1: Lock = Field(validation_alias="ox_IndctMzznHlyrdLck1_Ext")
    lock_2: Lock = Field(validation_alias="ox_IndctMzznHlyrdLck2_Ext")
    lock_3: Lock = Field(validation_alias="ox_IndctMzznHlyrdLck3_Ext")
    overhoist_full: Lock = Field(validation_alias="ox_IndctMzznHlyrdLckFhOvrhst_Ext")
    overhoist_1: Lock = Field(validation_alias="ox_IndctMzznHlyrdLck1Ovrhst_Ext")
    overhoist_2: Lock = Field(validation_alias="ox_IndctMzznHlyrdLck2Ovrhst_Ext")
    boom_lock_1: Lock = Field(validation_alias="ox_IndctMzznBmRfLck1_Ext")
    boom_lock_2: Lock = Field(validation_alias="ox_IndctMzznBmRfLck2_Ext")


class MizzenHeadsailLocks(LoadsModel, ABC):
    TOPIC = "sail-systems/f0401_mzznhdfrlr"
    lock: Lock = Field(validation_alias="ox_IndctHdslLck_Ext")
    overhoist: Lock = Field(validation_alias="ox_IndctHdslLckOvrhst_Ext")


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
