from loads.sensors import LoadsModel, at, sail_system


class MessagingModule:
    """Module handling one source of MQTT messages"""

    def __init__(self, models: list[type[LoadsModel]]) -> None:
        self._models = models
        self._mapping = {model.TOPIC: model for model in models}

    @property
    def topics(self) -> list[str]:
        return list(self._mapping.keys())

    def gen_config(self):
        return [model.gen_config() for model in self._models]


sail_system_sensors = MessagingModule(  # TODO: get from registry
    models=[
        sail_system.BladeAdjuster,
        sail_system.BladeCunningham,
        sail_system.BladeSheetCaptivePS,
        sail_system.BladeSheetCaptiveSB,
        sail_system.BladeSheetFeederPs,
        sail_system.BladeSheetFeederSb,
        sail_system.BladeTweakerPS,
        sail_system.BladeTweakerSB,
        sail_system.CodeSailTack,
        sail_system.HeadsailLocks,
        sail_system.MainCheckstayDeflector,
        sail_system.MainCunningham,
        sail_system.MainHalyard,
        sail_system.MainOuthaul,
        sail_system.MainPreventer,
        sail_system.MainRunnerSb,
        sail_system.MainRunnerPs,
        sail_system.MainSheet,
        sail_system.MainTraveler,
        sail_system.MainVang,
        sail_system.MizzenCheckstayDeflector,
        sail_system.MizzenCunningham,
        sail_system.MizzenHalyard,
        sail_system.MizzenHeadsailLocks,
        sail_system.MizzenHeadsailTackAdjuster,
        sail_system.MizzenOuthaul,
        sail_system.MizzenPreventer,
        sail_system.MizzenRunnerPs,
        sail_system.MizzenRunnerSb,
        sail_system.MizzenSheet,
        sail_system.MizzenVang,
        sail_system.PrimaryWinchPs,
        sail_system.PrimaryWinchSb,
        sail_system.StaysailSheetPs,
        sail_system.StaysailSheetSb,
        sail_system.StaysailSheetFeederPs,
        sail_system.StaysailSheetFeederSb,
        sail_system.StaysailStayAdjuster,
    ]
)


at_sensors = MessagingModule(
    models=[
        at.ApparentWindSpeed,
        at.ApparentWindAngle,
    ],
)
