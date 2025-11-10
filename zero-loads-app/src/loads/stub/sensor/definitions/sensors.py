# Based on FunctionList_Rev2
# https://docs.google.com/spreadsheets/d/1JdrFDqoArWxqEzr_02T6L84FTCKX7gj7/edit?usp=drive_link&ouid=103106168386399564004&rtpof=true&sd=true
from typing import Annotated

from .units import (
    Load,
    LoadsModel,
    Position,
    RelativePosition,
    RotationalSpeed,
    Temperature,
    Torque,
    component_meta,
)


class TensionCylinder(LoadsModel):
    """sTensionCylinder"""

    position: Position
    position_rel: RelativePosition
    load: Load


class FurlerElectric(LoadsModel):
    """sFurlerElectric"""

    torque: Torque
    speed: RotationalSpeed


class CaptiveWinch(LoadsModel):
    """sCaptiveWinch"""

    torque: Torque
    speed: RotationalSpeed
    temperature: Temperature


class TravelerWinch(LoadsModel):
    """sTravellerCaptive"""

    position_rel: RelativePosition
    load: Load


class BoomVang(LoadsModel):
    """sBoomVang"""

    load_bottom: Load
    load_rod: Load
    position: Position
    position_rel: RelativePosition


class SailSystems(LoadsModel):
    blade_cunningham: Annotated[TensionCylinder, component_meta(topic="F0101_BladeCunningham")]
    code_sail_tack: Annotated[TensionCylinder, component_meta(topic="F0102_CodeSailTack")]
    blade_adjuster: Annotated[TensionCylinder, component_meta(topic="F0103_BladeAdjuster")]
    staysail_stay_adjuster: Annotated[TensionCylinder, component_meta(topic="F0104_StaysailStayAdjuster")]
    main_outhaul: Annotated[TensionCylinder, component_meta(topic="F0201_MainOuthaul")]
    main_checkstay_deflector: Annotated[TensionCylinder, component_meta(topic="F0203_MainCheckstayDeflector")]
    main_boom_preventer: Annotated[TensionCylinder, component_meta(topic="F0204_MainBoomPreventer")]
    main_cunningham: Annotated[TensionCylinder, component_meta(topic="F0205_MainCunningham")]
    blade_tweaker_ps: Annotated[TensionCylinder, component_meta(topic="F0206_BladeTweakerPs")]
    blade_tweaker_sb: Annotated[TensionCylinder, component_meta(topic="F0207_BladeTweakerSb")]
    mizzen_headsail_tack_adjuster: Annotated[TensionCylinder, component_meta(topic="F0402_MizzenHeadsailTackAdjuster")]
    mizzen_outhaul: Annotated[TensionCylinder, component_meta(topic="F0501_MizzenOuthaul")]

    mizzen_checkstay_adjuster: Annotated[TensionCylinder, component_meta(topic="F0503_MizzenCheckstayDeflector")]
    mizzen_cunningham: Annotated[TensionCylinder, component_meta(topic="F0504_MizzenCunningham")]
    mizzen_boom_preventer: Annotated[TensionCylinder, component_meta(topic="F0506_MizzenBoomPreventer")]

    blade_furler: Annotated[FurlerElectric, component_meta(topic="FE102_BladeFurler")]
    staysail_furler: Annotated[FurlerElectric, component_meta(topic="FE103_StaysailFurler")]
    code_furler: Annotated[FurlerElectric, component_meta(topic="FE101_CodeFurler")]

    blade_sheet_captive_winch_ps: Annotated[CaptiveWinch, component_meta(topic="FE201_BladeSheetCaptiveWinchPs")]
    staysail_sheet_captive_winch_ps: Annotated[CaptiveWinch, component_meta(topic="FE203_StaysailSheetCaptiveWinchPs")]
    main_sheet_captive_winch: Annotated[CaptiveWinch, component_meta(topic="FE205_MainSheetCaptiveWinch")]
    main_halyard_captive_winch: Annotated[CaptiveWinch, component_meta(topic="FE207_MainHalyardCaptiveWinch")]
    blade_sheet_captive_winch_sb: Annotated[CaptiveWinch, component_meta(topic="FE301_BladeSheetCaptiveWinchSb")]
    staysail_sheet_captive_winch_sb: Annotated[CaptiveWinch, component_meta(topic="FE303_StaysailSheetCaptiveWinchSb")]
    main_runner_captive_winch_ps: Annotated[CaptiveWinch, component_meta(topic="FE401_MainRunnerCaptiveWinchPs")]
    mizzen_runner_captive_winch_ps: Annotated[CaptiveWinch, component_meta(topic="FE402_MizzenRunnerCaptiveWinchPs")]
    mizzen_halyard_captive_winch: Annotated[CaptiveWinch, component_meta(topic="FE404_MizzenHalyardCaptiveWinch")]
    main_runner_captive_winch_sb: Annotated[CaptiveWinch, component_meta(topic="FE501_MainRunnerCaptiveWinchSb")]
    mizzen_runner_captive_winch_sb: Annotated[CaptiveWinch, component_meta(topic="FE502_MizzenRunnerCaptiveWinchSb")]
    mizzen_sheet_captive_winch: Annotated[CaptiveWinch, component_meta(topic="FE504_MizzenSheetCaptiveWinch")]

    main_vang: Annotated[BoomVang, component_meta(topic="F0202_MainVang")]
    mizzen_vang: Annotated[BoomVang, component_meta(topic="F0502_MizzenVang")]
