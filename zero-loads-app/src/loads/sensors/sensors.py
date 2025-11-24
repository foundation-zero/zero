# Based on Sail-Hydraulic PLC IO List

from .base import LoadsModel
from .units import (
    Load,
    Position,
    RelativePosition,
    RotationalSpeed,
    Temperature,
    Torque,
)


class TensionCylinder(LoadsModel):
    """sTensionCylinder"""

    ow_ActPos_mm: Position
    ow_ActPos2_mm: Position
    ow_ActPos_pm: RelativePosition
    ow_ActPos2_pm: RelativePosition
    ow_ActLoad_10kg: Load


class FurlerElectric(LoadsModel):
    """sFurlerElectric"""

    ii_ActTrq: Torque
    ii_ActSpd: RotationalSpeed


class CaptiveWinch(LoadsModel):
    """sCaptiveWinch"""

    ii_ActTrq: Torque
    ii_ActSpd: RotationalSpeed
    ii_IgbtTemp: Temperature


class BoomVang(LoadsModel):
    """sBoomVang"""

    ow_ActLoad_10kg: Load
    ow_ActLoad2_10kg: Load
    ow_ActPos_mm: Position
    ow_ActPos_pm: RelativePosition


class BladeCunningham(LoadsModel):
    TOPIC = "sail-systems/f0101_bldcnnnghm"
    blade_cunningham: TensionCylinder


class CodeSailTack(LoadsModel):
    TOPIC = "sail-systems/f0102_cdtckcyl"
    code_sail_tack: TensionCylinder


class BladeAdjuster(LoadsModel):
    TOPIC = "sail-systems/f0103_bldadjstr"
    blade_adjuster: TensionCylinder


class StaysailStayAdjuster(LoadsModel):
    TOPIC = "sail-systems/f0104_stysladjstr"
    staysail_stay_adjuster: TensionCylinder


class MainOuthaul(LoadsModel):
    TOPIC = "sail-systems/f0201_mnothl"
    main_outhaul: TensionCylinder


class MainCheckstayDeflector(LoadsModel):
    TOPIC = "sail-systems/f0203_mnchckstydflctr"
    main_checkstay_deflector: TensionCylinder


class MainBoomPreventer(LoadsModel):
    TOPIC = "sail-systems/f0204_mnbmprvntr"
    main_boom_preventer: TensionCylinder


class MainCunningham(LoadsModel):
    TOPIC = "sail-systems/f0205_mncnnnghm"
    main_cunningham: TensionCylinder


class BladeTweakerPS(LoadsModel):
    TOPIC = "sail-systems/f0206_bldtwkrps"
    blade_tweaker_ps: TensionCylinder


class BladeTweakerSB(LoadsModel):
    TOPIC = "sail-systems/f0207_bldtwkrsb"
    blade_tweaker_sb: TensionCylinder


class MizzenHeadsailTackAdjuster(LoadsModel):
    TOPIC = "sail-systems/f0402_mzznhdsladjstr"
    mizzen_headsail_tack_adjuster: TensionCylinder


class MizzenOuthaul(LoadsModel):
    TOPIC = "sail-systems/f0501_mzznothl"
    mizzen_outhaul: TensionCylinder


class MizzenCheckstayAdjuster(LoadsModel):
    TOPIC = "sail-systems/f0503_mzznchckstydflctr"
    mizzen_checkstay_adjuster: TensionCylinder


class MizzenCunningham(LoadsModel):
    TOPIC = "sail-systems/f0504_mzzncnnnghm"
    mizzen_cunningham: TensionCylinder


class MizzenBoomPreventer(LoadsModel):
    TOPIC = "sail-systems/f0506_mzznbmprvntr"
    mizzen_boom_preventer: TensionCylinder


class BladeFurler(LoadsModel):
    TOPIC = "sail-systems/fe102_bldfrlr"
    blade_furler: FurlerElectric


class StaysailFurler(LoadsModel):
    TOPIC = "sail-systems/fe103_styslfrlr"
    staysail_furler: FurlerElectric


class CodeFurler(LoadsModel):
    TOPIC = "sail-systems/fe101_cdzrfrlr"
    code_furler: FurlerElectric


class BladeSheetCaptiveWinchPS(LoadsModel):
    TOPIC = "sail-systems/fe201_bldshtps"
    blade_sheet_captive_winch_ps: CaptiveWinch


class StaysailSheetCaptiveWinchPS(LoadsModel):
    TOPIC = "sail-systems/fe203_styslshtps"
    staysail_sheet_captive_winch_ps: CaptiveWinch


class MainSheetCaptiveWinch(LoadsModel):
    TOPIC = "sail-systems/fe205_mnsht"
    main_sheet_captive_winch: CaptiveWinch


class MainHalyardCaptiveWinch(LoadsModel):
    TOPIC = "sail-systems/fe207_mnhlyrd"
    main_halyard_captive_winch: CaptiveWinch


class BladeSheetCaptiveWinchSB(LoadsModel):
    TOPIC = "sail-systems/fe301_bldshtsb"
    blade_sheet_captive_winch_sb: CaptiveWinch


class StaysailSheetCaptiveWinchSB(LoadsModel):
    TOPIC = "sail-systems/fe303_styslshtsb"
    staysail_sheet_captive_winch_sb: CaptiveWinch


class MainRunnerCaptiveWinchPS(LoadsModel):
    TOPIC = "sail-systems/fe401_mnrnnrps"
    main_runner_captive_winch_ps: CaptiveWinch


class MizzenRunnerCaptiveWinchPS(LoadsModel):
    TOPIC = "sail-systems/fe402_mzznrnnrps"
    mizzen_runner_captive_winch_ps: CaptiveWinch


class MizzenHalyardCaptiveWinch(LoadsModel):
    TOPIC = "sail-systems/fe404_mzznhlyrd"
    mizzen_halyard_captive_winch: CaptiveWinch


class MainRunnerCaptiveWinchSB(LoadsModel):
    TOPIC = "sail-systems/fe501_mnrnnrsb"
    main_runner_captive_winch_sb: CaptiveWinch


class MizzenRunnerCaptiveWinchSB(LoadsModel):
    TOPIC = "sail-systems/fe502_mzznrnnrsb"
    mizzen_runner_captive_winch_sb: CaptiveWinch


class MizzenSheetCaptiveWinch(LoadsModel):
    TOPIC = "sail-systems/fe504_mzznsht"
    mizzen_sheet_captive_winch: CaptiveWinch


class MainVang(LoadsModel):
    TOPIC = "sail-systems/f0202_mnbmvng"
    main_vang: BoomVang


class MizzenVang(LoadsModel):
    TOPIC = "sail-systems/f0502_mzznbmvng"
    mizzen_vang: BoomVang
