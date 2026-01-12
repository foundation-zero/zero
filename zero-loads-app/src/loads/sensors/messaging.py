import loads.sensors.sensors as sensors
from loads.sensors import LoadsModel


class MessagingModule:
    """Module handling multiple validators."""

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
        sensors.BladeAdjuster,
        sensors.BladeCunningham,
        sensors.BladeSheetCaptivePS,
        sensors.BladeSheetCaptiveSB,
        sensors.BladeSheetFeederPs,
        sensors.BladeSheetFeederSb,
        sensors.BladeTweakerPS,
        sensors.BladeTweakerSB,
        sensors.CodeSailTack,
        sensors.HeadsailLocks,
        sensors.MainCheckstayDeflector,
        sensors.MainCunningham,
        sensors.MainHalyard,
        sensors.MainOuthaul,
        sensors.MainPreventer,
        sensors.MainRunnerCaptivePS,
        sensors.MainRunnerCaptiveSB,
        sensors.MainSheetCaptive,
        sensors.MainVang,
        sensors.MizzenCheckstayDeflector,
        sensors.MizzenCunningham,
        sensors.MizzenHalyard,
        sensors.MizzenHeadsailLocks,
        sensors.MizzenHeadsailTackAdjuster,
        sensors.MizzenOuthaul,
        sensors.MizzenPreventer,
        sensors.MizzenRunnerCaptivePS,
        sensors.MizzenRunnerCaptiveSB,
        sensors.MizzenSheetCaptive,
        sensors.MizzenVang,
        sensors.StaysailSheetCaptivePS,
        sensors.StaysailSheetCaptiveSB,
        sensors.StaysailSheetFeederPs,
        sensors.StaysailSheetFeederSb,
        sensors.StaysailStayAdjuster,
    ]
)
