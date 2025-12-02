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
    blade_cunningham: Annotated[
        TensionCylinder, component_meta(topic="f0101-bladecunningham")
    ]
    code_sail_tack: Annotated[
        TensionCylinder, component_meta(topic="f0102-codesailtack")
    ]
    blade_adjuster: Annotated[
        TensionCylinder, component_meta(topic="f0103-bladeadjuster")
    ]
    staysail_stay_adjuster: Annotated[
        TensionCylinder, component_meta(topic="f0104-staysailstayadjuster")
    ]
    main_outhaul: Annotated[TensionCylinder, component_meta(topic="f0201-mainouthaul")]
    main_checkstay_deflector: Annotated[
        TensionCylinder, component_meta(topic="f0203-maincheckstaydeflector")
    ]
    main_boom_preventer: Annotated[
        TensionCylinder, component_meta(topic="f0204-mainboompreventer")
    ]
    main_cunningham: Annotated[
        TensionCylinder, component_meta(topic="f0205-maincunningham")
    ]
    blade_tweaker_ps: Annotated[
        TensionCylinder, component_meta(topic="f0206-bladetweakerps")
    ]
    blade_tweaker_sb: Annotated[
        TensionCylinder, component_meta(topic="f0207-bladetweakersb")
    ]
    mizzen_headsail_tack_adjuster: Annotated[
        TensionCylinder, component_meta(topic="f0402-mizzenheadsailtackadjuster")
    ]
    mizzen_outhaul: Annotated[
        TensionCylinder, component_meta(topic="f0501-mizzenouthaul")
    ]

    mizzen_checkstay_adjuster: Annotated[
        TensionCylinder, component_meta(topic="f0503-mizzencheckstaydeflector")
    ]
    mizzen_cunningham: Annotated[
        TensionCylinder, component_meta(topic="f0504-mizzencunningham")
    ]
    mizzen_boom_preventer: Annotated[
        TensionCylinder, component_meta(topic="f0506-mizzenboompreventer")
    ]

    blade_furler: Annotated[FurlerElectric, component_meta(topic="fe102-bladefurler")]
    staysail_furler: Annotated[
        FurlerElectric, component_meta(topic="fe103-staysailfurler")
    ]
    code_furler: Annotated[FurlerElectric, component_meta(topic="fe101-codefurler")]

    blade_sheet_captive_winch_ps: Annotated[
        CaptiveWinch, component_meta(topic="fe201-bladesheetcaptivewinchps")
    ]
    staysail_sheet_captive_winch_ps: Annotated[
        CaptiveWinch, component_meta(topic="fe203-staysailsheetcaptivewinchps")
    ]
    main_sheet_captive_winch: Annotated[
        CaptiveWinch, component_meta(topic="fe205-mainsheetcaptivewinch")
    ]
    main_halyard_captive_winch: Annotated[
        CaptiveWinch, component_meta(topic="fe207-mainhalyardcaptivewinch")
    ]
    blade_sheet_captive_winch_sb: Annotated[
        CaptiveWinch, component_meta(topic="fe301-bladesheetcaptivewinchsb")
    ]
    staysail_sheet_captive_winch_sb: Annotated[
        CaptiveWinch, component_meta(topic="fe303-staysailsheetcaptivewinchsb")
    ]
    main_runner_captive_winch_ps: Annotated[
        CaptiveWinch, component_meta(topic="fe401-mainrunnercaptivewinchps")
    ]
    mizzen_runner_captive_winch_ps: Annotated[
        CaptiveWinch, component_meta(topic="fe402-mizzenrunnercaptivewinchps")
    ]
    mizzen_halyard_captive_winch: Annotated[
        CaptiveWinch, component_meta(topic="fe404-mizzenhalyardcaptivewinch")
    ]
    main_runner_captive_winch_sb: Annotated[
        CaptiveWinch, component_meta(topic="fe501-mainrunnercaptivewinchsb")
    ]
    mizzen_runner_captive_winch_sb: Annotated[
        CaptiveWinch, component_meta(topic="fe502-mizzenrunnercaptivewinchsb")
    ]
    mizzen_sheet_captive_winch: Annotated[
        CaptiveWinch, component_meta(topic="fe504-mizzensheetcaptivewinch")
    ]

    main_vang: Annotated[BoomVang, component_meta(topic="f0202-mainvang")]
    mizzen_vang: Annotated[BoomVang, component_meta(topic="f0502-mizzenvang")]
