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


class TensionCylinder(LoadsModel):
    ow_ActPos_mm: Position = Field(serialization_alias="ow_actpos_mm")
    ow_ActPos2_mm: Position = Field(serialization_alias="ow_actpos2_mm")
    ow_ActPos_pm: RelativePosition = Field(serialization_alias="ow_actpos_pm")
    ow_ActPos2_pm: RelativePosition = Field(serialization_alias="ow_actpos2_pm")
    ow_ActLoad_10kg: Load = Field(serialization_alias="ow_actload_10kg")

    @property
    def load(self) -> Load:
        return self.ow_ActLoad_10kg

    @property
    def position(self) -> Position:
        return self.ow_ActPos_mm

    @property
    def position_2(self) -> Position:
        return self.ow_ActPos2_mm

    @property
    def relative_position(self) -> RelativePosition:
        return self.ow_ActPos_pm

    @property
    def relative_position_2(self) -> RelativePosition:
        return self.ow_ActPos2_pm


class FurlerElectric(LoadsModel, ABC):
    ii_ActTrq: Torque = Field(serialization_alias="ii_acttrq")
    ii_ActSpd: RotationalSpeed = Field(serialization_alias="ii_actspd")

    @property
    def torque(self) -> Torque:
        return self.ii_ActTrq

    @property
    def rotational_speed(self) -> RotationalSpeed:
        return self.ii_ActSpd


class CaptiveWinch(LoadsModel, ABC):
    ii_ActTrq: Torque = Field(serialization_alias="ii_acttrq")
    ii_ActSpd: RotationalSpeed = Field(serialization_alias="ii_actspd")
    ii_IgbtTemp: Temperature = Field(serialization_alias="ii_igbttemp")

    @property
    def torque(self) -> Torque:
        return self.ii_ActTrq

    @property
    def rotational_speed(self) -> RotationalSpeed:
        return self.ii_ActSpd

    @property
    def temperature(self) -> Temperature:
        return self.ii_IgbtTemp


class BoomVang(LoadsModel, ABC):
    ow_ActLoad_10kg: Load = Field(serialization_alias="ow_actload_10kg")
    ow_ActLoad2_10kg: Load = Field(serialization_alias="ow_actload2_10kg")
    ow_ActPos_mm: Position = Field(serialization_alias="ow_actpos_mm")
    ow_ActPos_pm: RelativePosition = Field(serialization_alias="ow_actpos_pm")

    @property
    def load(self) -> Load:
        return self.ow_ActLoad_10kg

    @property
    def load_2(self) -> Load:
        return self.ow_ActLoad2_10kg

    @property
    def position(self) -> Position:
        return self.ow_ActPos_mm

    @property
    def relative_position(self) -> RelativePosition:
        return self.ow_ActPos_pm


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
