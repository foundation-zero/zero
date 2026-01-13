from loads.sensors import LoadsModel, at, sails


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
        sails.BladeAdjuster,
        sails.BladeCunningham,
        sails.BladeSheetCaptivePS,
        sails.BladeSheetCaptiveSB,
        sails.BladeSheetFeederPs,
        sails.BladeSheetFeederSb,
        sails.BladeTweakerPS,
        sails.BladeTweakerSB,
        sails.CodeSailTack,
        sails.HeadsailLocks,
        sails.MainCheckstayDeflector,
        sails.MainCunningham,
        sails.MainHalyard,
        sails.MainOuthaul,
        sails.MainPreventer,
        sails.MainRunnerCaptivePS,
        sails.MainRunnerCaptiveSB,
        sails.MainSheetCaptive,
        sails.MainVang,
        sails.MizzenCheckstayDeflector,
        sails.MizzenCunningham,
        sails.MizzenHalyard,
        sails.MizzenHeadsailLocks,
        sails.MizzenHeadsailTackAdjuster,
        sails.MizzenOuthaul,
        sails.MizzenPreventer,
        sails.MizzenRunnerCaptivePS,
        sails.MizzenRunnerCaptiveSB,
        sails.MizzenSheetCaptive,
        sails.MizzenVang,
        sails.StaysailSheetCaptivePS,
        sails.StaysailSheetCaptiveSB,
        sails.StaysailSheetFeederPs,
        sails.StaysailSheetFeederSb,
        sails.StaysailStayAdjuster,
    ]
)


at_systems = MessagingModule(
    validators=[
        at.SystemLatitude,
        at.SystemLongitude,
        at.SystemBoatSpeedKts,
        at.UTCDate,
    ],
)
