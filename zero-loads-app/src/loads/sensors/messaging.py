import loads.sensors.sensors as sensors
from loads.sensors import LoadsModel


class MessagingModule:
    """Module handling multiple validators for different topics."""

    def __init__(self, validators: list[type[LoadsModel]]) -> None:
        self._validators = validators
        self._mapping = {validator.TOPIC: validator for validator in validators}

    @property
    def topics(self) -> list[str]:
        return list(self._mapping.keys())

    def gen_config(self):
        return [validator.gen_config() for validator in self._validators]


sail_systems = MessagingModule(
    validators=[
        sensors.BladeCunningham,
        sensors.CodeSailTack,
        sensors.BladeAdjuster,
        sensors.StaysailStayAdjuster,
        sensors.MainOuthaul,
        sensors.MainCheckstayDeflector,
        sensors.MainBoomPreventer,
        sensors.MainCunningham,
        sensors.BladeTweakerPS,
        sensors.BladeTweakerSB,
        sensors.MizzenHeadsailTackAdjuster,
        sensors.MizzenOuthaul,
        sensors.MizzenCheckstayAdjuster,
        sensors.MizzenCunningham,
        sensors.MizzenBoomPreventer,
        sensors.BladeFurler,
        sensors.StaysailFurler,
        sensors.CodeFurler,
        sensors.BladeSheetCaptiveWinchPS,
        sensors.StaysailSheetCaptiveWinchPS,
        sensors.MainSheetCaptiveWinch,
        sensors.MainHalyardCaptiveWinch,
        sensors.BladeSheetCaptiveWinchSB,
        sensors.StaysailSheetCaptiveWinchSB,
        sensors.MainRunnerCaptiveWinchPS,
        sensors.MizzenRunnerCaptiveWinchPS,
        sensors.MizzenHalyardCaptiveWinch,
        sensors.MainRunnerCaptiveWinchSB,
        sensors.MizzenRunnerCaptiveWinchSB,
        sensors.MizzenSheetCaptiveWinch,
        sensors.MainVang,
        sensors.MizzenVang,
    ]
)
