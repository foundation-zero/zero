from loads.sensors import LoadsModel, at, plc


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


plc_sensors = MessagingModule(
    validators=[
        plc.BladeAdjuster,
        plc.BladeCunningham,
        plc.BladeSheetCaptivePS,
        plc.BladeSheetCaptiveSB,
        plc.BladeSheetFeederPs,
        plc.BladeSheetFeederSb,
        plc.BladeTweakerPS,
        plc.BladeTweakerSB,
        plc.CodeSailTack,
        plc.HeadsailLocks,
        plc.MainCheckstayDeflector,
        plc.MainCunningham,
        plc.MainHalyard,
        plc.MainOuthaul,
        plc.MainPreventer,
        plc.MainRunnerCaptivePS,
        plc.MainRunnerCaptiveSB,
        plc.MainSheetCaptive,
        plc.MainVang,
        plc.MizzenCheckstayDeflector,
        plc.MizzenCunningham,
        plc.MizzenHalyard,
        plc.MizzenHeadsailLocks,
        plc.MizzenHeadsailTackAdjuster,
        plc.MizzenOuthaul,
        plc.MizzenPreventer,
        plc.MizzenRunnerCaptivePS,
        plc.MizzenRunnerCaptiveSB,
        plc.MizzenSheetCaptive,
        plc.MizzenVang,
        plc.StaysailSheetCaptivePS,
        plc.StaysailSheetCaptiveSB,
        plc.StaysailSheetFeederPs,
        plc.StaysailSheetFeederSb,
        plc.StaysailStayAdjuster,
    ]
)


at_sensors = MessagingModule(
    validators=[
        at.ApparentWindSpeed,
        at.ApparentWindAngle,
    ],
)
