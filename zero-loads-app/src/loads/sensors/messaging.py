import loads.sensors.sensors as sensors
from loads.api.messaging import MessagingModule

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
