from abc import ABC

from pydantic import Field

from .base import LoadsModel
from .units import (
    Load,
    Position,
    RelativePosition,
    RotationalSpeed,
    Temperature,
    Torque,
)


class TensionCylinder(LoadsModel, ABC):
    ow_actpos_mm: Position = Field(validation_alias="ow_ActPos_mm")
    ow_actpos2_mm: Position = Field(validation_alias="ow_ActPos2_mm")
    ow_actpos_pm: RelativePosition = Field(validation_alias="ow_ActPos_pm")
    ow_actpos2_pm: RelativePosition = Field(validation_alias="ow_ActPos2_pm")
    ow_actload_10kg: Load = Field(validation_alias="ow_ActLoad_10kg")

    @property
    def load(self) -> Load:
        return self.ow_actload_10kg

    @property
    def position(self) -> Position:
        return self.ow_actpos_mm

    @property
    def position_2(self) -> Position:
        return self.ow_actpos2_mm

    @property
    def relative_position(self) -> RelativePosition:
        return self.ow_actpos_pm

    @property
    def relative_position_2(self) -> RelativePosition:
        return self.ow_actpos2_pm


class FurlerElectric(LoadsModel, ABC):
    ii_acttrq: Torque = Field(alias="ii_ActTrq")
    ii_actspd: RotationalSpeed = Field(alias="ii_ActSpd")

    @property
    def torque(self) -> Torque:
        return self.ii_acttrq

    @property
    def rotational_speed(self) -> RotationalSpeed:
        return self.ii_actspd


class CaptiveWinch(LoadsModel, ABC):
    ii_acttrq: Torque = Field(validation_alias="ii_ActTrq")
    ii_actspd: RotationalSpeed = Field(validation_alias="ii_ActSpd")
    ii_igbttemp: Temperature = Field(validation_alias="ii_IgbtTemp")

    @property
    def torque(self) -> Torque:
        return self.ii_acttrq

    @property
    def rotational_speed(self) -> RotationalSpeed:
        return self.ii_actspd

    @property
    def temperature(self) -> Temperature:
        return self.ii_igbttemp


class BoomVang(LoadsModel, ABC):
    ow_actload_10kg: Load = Field(validation_alias="ow_ActLoad_10kg")
    ow_actload2_10kg: Load = Field(validation_alias="ow_ActLoad2_10kg")
    ow_actpos_mm: Position = Field(validation_alias="ow_ActPos_mm")
    ow_actpos_pm: RelativePosition = Field(validation_alias="ow_ActPos_pm")

    @property
    def load(self) -> Load:
        return self.ow_actload_10kg

    @property
    def load_2(self) -> Load:
        return self.ow_actload2_10kg

    @property
    def position(self) -> Position:
        return self.ow_actpos_mm

    @property
    def relative_position(self) -> RelativePosition:
        return self.ow_actpos_pm


class BladeCunningham(TensionCylinder):
    TOPIC = "sail-systems/f0101_bldcnnnghm"


class CodeSailTack(TensionCylinder):
    TOPIC = "sail-systems/f0102_cdtckcyl"


class BladeAdjuster(TensionCylinder):
    TOPIC = "sail-systems/f0103_bldadjstr"


class StaysailStayAdjuster(TensionCylinder):
    TOPIC = "sail-systems/f0104_stysladjstr"


class MainOuthaul(TensionCylinder):
    TOPIC = "sail-systems/f0201_mnothl"


class MainCheckstayDeflector(TensionCylinder):
    TOPIC = "sail-systems/f0203_mnchckstydflctr"


class MainBoomPreventer(TensionCylinder):
    TOPIC = "sail-systems/f0204_mnbmprvntr"


class MainCunningham(TensionCylinder):
    TOPIC = "sail-systems/f0205_mncnnnghm"


class BladeTweakerPS(TensionCylinder):
    TOPIC = "sail-systems/f0206_bldtwkrps"


class BladeTweakerSB(TensionCylinder):
    TOPIC = "sail-systems/f0207_bldtwkrsb"


class MizzenHeadsailTackAdjuster(TensionCylinder):
    TOPIC = "sail-systems/f0402_mzznhdsladjstr"


class MizzenOuthaul(TensionCylinder):
    TOPIC = "sail-systems/f0501_mzznothl"


class MizzenCheckstayAdjuster(TensionCylinder):
    TOPIC = "sail-systems/f0503_mzznchckstydflctr"


class MizzenCunningham(TensionCylinder):
    TOPIC = "sail-systems/f0504_mzzncnnnghm"


class MizzenBoomPreventer(TensionCylinder):
    TOPIC = "sail-systems/f0506_mzznbmprvntr"


class BladeFurler(FurlerElectric):
    TOPIC = "sail-systems/fe102_bldfrlr"


class StaysailFurler(FurlerElectric):
    TOPIC = "sail-systems/fe103_styslfrlr"


class CodeFurler(FurlerElectric):
    TOPIC = "sail-systems/fe101_cdzrfrlr"


class BladeSheetCaptiveWinchPS(CaptiveWinch):
    TOPIC = "sail-systems/fe201_bldshtps"


class StaysailSheetCaptiveWinchPS(CaptiveWinch):
    TOPIC = "sail-systems/fe203_styslshtps"


class MainSheetCaptiveWinch(CaptiveWinch):
    TOPIC = "sail-systems/fe205_mnsht"


class MainHalyardCaptiveWinch(CaptiveWinch):
    TOPIC = "sail-systems/fe207_mnhlyrd"


class BladeSheetCaptiveWinchSB(CaptiveWinch):
    TOPIC = "sail-systems/fe301_bldshtsb"


class StaysailSheetCaptiveWinchSB(CaptiveWinch):
    TOPIC = "sail-systems/fe303_styslshtsb"


class MainRunnerCaptiveWinchPS(CaptiveWinch):
    TOPIC = "sail-systems/fe401_mnrnnrps"


class MizzenRunnerCaptiveWinchPS(CaptiveWinch):
    TOPIC = "sail-systems/fe402_mzznrnnrps"


class MizzenHalyardCaptiveWinch(CaptiveWinch):
    TOPIC = "sail-systems/fe404_mzznhlyrd"


class MainRunnerCaptiveWinchSB(CaptiveWinch):
    TOPIC = "sail-systems/fe501_mnrnnrsb"


class MizzenRunnerCaptiveWinchSB(CaptiveWinch):
    TOPIC = "sail-systems/fe502_mzznrnnrsb"


class MizzenSheetCaptiveWinch(CaptiveWinch):
    TOPIC = "sail-systems/fe504_mzznsht"


class MainVang(BoomVang):
    TOPIC = "sail-systems/f0202_mnbmvng"


class MizzenVang(BoomVang):
    TOPIC = "sail-systems/f0502_mzznbmvng"
