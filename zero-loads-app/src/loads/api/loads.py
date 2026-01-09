from typing import Any, Callable, Literal, Protocol

import loads.sensors.sensors as sensors
from loads.sensors import LoadsModel

Fields = Literal[
    "torque",
    "load",
    "load_ps",
    "load_sb",
    "position",
    "relative_position",
    "lock",
    "lock_full",
    "lock_1",
    "lock_2",
    "lock_3",
    "overhoist",
    "overhoist_full",
    "overhoist_1",
    "overhoist_2",
    "overhoist_3",
]


class LoadsField[T: LoadsModel](Protocol):
    model: type[T]

    def give(self, data: T) -> Any: ...


class LoadField[T: LoadsModel]:
    def __init__(self, model: type[T], field: Fields) -> None:
        self.model = model
        self._field = field

    def give(self, data: T | None) -> float | None:
        return getattr(data, self._field) if data else None


class FnField[T: LoadsModel]:
    def __init__(self, model: type[T], fn: Callable[[T], float]) -> None:
        self.model = model
        self._fn = fn

    def give(self, data: T | None) -> float | None:
        if data:
            return self._fn(data)
        else:
            return None


loads_variables: dict[str, LoadsField] = {
    "blade-adjuster-load": LoadField(sensors.BladeAdjuster, "load"),
    "blade-adjuster-position": LoadField(sensors.BladeAdjuster, "position"),
    "blade-cunningham-load": LoadField(sensors.BladeCunningham, "load"),
    #'blade-cunningham-position-1': LoadField(sensors.BladeCunningham, "position_1"),#what are pos 1 and 2?
    #'blade-cunningham-position-2': LoadField(sensors.BladeCunningham, "position_2"),
    "blade-sheet-feeder-ps-load": LoadField(sensors.BladeSheetFeederPs, "load"),
    "blade-sheet-feeder-sb-load": LoadField(sensors.BladeSheetFeederSb, "load"),
    "blade-tweaker-ps-load": LoadField(sensors.BladeTweakerPS, "load"),
    "blade-tweaker-ps-position": LoadField(sensors.BladeTweakerPS, "position"),
    "blade-tweaker-sb-load": LoadField(sensors.BladeTweakerSB, "load"),
    "blade-tweaker-sb-position": LoadField(sensors.BladeTweakerSB, "position"),
    "code-zero-lock": LoadField(sensors.HeadsailLocks, "lock"),
    "code-zero-overhoist": LoadField(sensors.HeadsailLocks, "overhoist"),
    "code-zero-tack-load": LoadField(sensors.CodeSailTack, "load"),
    #'code-zero-tack-position-1': LoadField(sensors.CodeSailTack, "position_1"),#what's position 1 and 2?
    #'code-zero-tack-position-2': LoadField(sensors.CodeSailTack, "position_2"),
    "main-boom-reef-1-lock": LoadField(sensors.MainHalyard, "lock_1"),
    "main-boom-reef-2-lock": LoadField(sensors.MainHalyard, "lock_2"),
    "main-boom-reef-3-lock": LoadField(sensors.MainHalyard, "lock_3"),
    "main-checkstay-deflector-ps-load": LoadField(
        sensors.MainCheckstayDeflector, "load_ps"
    ),
    "main-checkstay-deflector-sb-load": LoadField(
        sensors.MainCheckstayDeflector, "load_sb"
    ),
    #'main-checkstay-deflector-ps-position': LoadsField(sensors.MainCheckStayDeflector, "position_ps")#no differentiation between ps an sb position
    #'main-checkstay-deflector-sb-position': LoadsField(sensors.MainCheckStayDeflector, "position_sb")#no differentiation between ps an sb position
    #'main-checkstay-ps-load': #where's the loadpin?
    #'main-checkstay-sb-load': #where's the loadpin?
    "main-cunningham-load": LoadField(sensors.MainCunningham, "load"),
    "main-cunningham-position": LoadField(sensors.MainCunningham, "position"),
    "main-halyard-load": LoadField(sensors.MainHalyard, "load"),
    "main-halyard-lock-full": LoadField(sensors.MainHalyard, "lock_full"),
    "main-halyard-overhoist-full": LoadField(sensors.MainHalyard, "overhoist_full"),
    "main-halyard-reef-1-lock": LoadField(sensors.MainHalyard, "lock_1"),
    "main-halyard-reef-1-overhoist": LoadField(sensors.MainHalyard, "overhoist_1"),
    "main-halyard-reef-2-lock": LoadField(sensors.MainHalyard, "lock_2"),
    "main-halyard-reef-2-overhoist": LoadField(sensors.MainHalyard, "overhoist_2"),
    "main-halyard-reef-3-lock": LoadField(sensors.MainHalyard, "lock_3"),
    "main-halyard-reef-3-overhoist": LoadField(sensors.MainHalyard, "overhoist_3"),
    "main-halyard-rel-position": LoadField(sensors.MainHalyard, "relative_position"),
    "main-outhaul-load": LoadField(sensors.MainOuthaul, "load"),
    "main-outhaul-position": LoadField(sensors.MainOuthaul, "position"),
    "main-preventer-load": LoadField(sensors.MainPreventer, "load"),
    "main-preventer-position": LoadField(sensors.MainPreventer, "position"),
    "main-runner-ps-rel-position": LoadField(
        sensors.MainRunnerCaptivePS, "relative_position"
    ),
    #'main-runner-ps-load': #where's the loadpin?
    "main-runner-sb-rel-position": LoadField(
        sensors.MainRunnerCaptiveSB, "relative_position"
    ),
    #'main-runner-sb-load': #where's the loadpin?
    #'main-sheet-load':#where's the loadpin?
    #'main-traveler-position': #where's the traveler?
    "main-vang-position": LoadField(sensors.MainVang, "position"),
    #'main-vang-load': LoadField(sensors.MainVang, "load"),#bottom or rod?
    "mizzen-boom-reef-1-lock": LoadField(sensors.MizzenHalyard, "lock_1"),
    "mizzen-boom-reef-2-lock": LoadField(sensors.MizzenHalyard, "lock_2"),
    "mizzen-checkstay-deflector-ps-load": LoadField(
        sensors.MizzenCheckstayDeflector, "load_ps"
    ),
    #'mizzen-checkstay-deflector-ps-position: LoadField(sensors.MizzenCheckstayDeflector, "position_ps"), # no differentiation between ps an sb position
    "mizzen-checkstay-deflector-sb-load": LoadField(
        sensors.MizzenCheckstayDeflector, "load_sb"
    ),
    #'mizzen-checkstay-deflector-sb-position: LoadField(sensors.MizzenCheckstayDeflector, "position_sb"), # no differentiation between ps an sb position
    #'mizzen-checkstay-ps-load': #where's the loadpin?
    #'mizzen-checkstay-sb-load': #where's the loadpin?
    "mizzen-cunningham-load": LoadField(sensors.MizzenCunningham, "load"),
    "mizzen-cunningham-position": LoadField(sensors.MizzenCunningham, "position"),
    "mizzen-halyard-load": LoadField(sensors.MizzenHalyard, "load"),
    "mizzen-halyard-position": LoadField(sensors.MizzenHalyard, "position"),
    "mizzen-headsail-lock": LoadField(sensors.MizzenHeadsailLocks, "lock"),
    "mizzen-headsail-overhoist": LoadField(sensors.MizzenHeadsailLocks, "overhoist"),
    "mizzen-headsail-tack-adjuster-load": LoadField(
        sensors.MizzenHeadsailTackAdjuster, "load"
    ),
    "mizzen-headsail-tack-adjuster-position": LoadField(
        sensors.MizzenHeadsailTackAdjuster, "position"
    ),
    "mizzen-outhaul-load": LoadField(sensors.MizzenOuthaul, "load"),
    "mizzen-outhaul-position": LoadField(sensors.MizzenOuthaul, "position"),
    "mizzen-preventer-load": LoadField(sensors.MizzenPreventer, "load"),
    "mizzen-preventer-position": LoadField(sensors.MizzenPreventer, "position"),
    "mizzen-reef-1-lock": LoadField(sensors.MizzenHalyard, "lock_1"),
    "mizzen-reef-1-overhoist": LoadField(sensors.MizzenHalyard, "overhoist_1"),
    "mizzen-reef-2-lock": LoadField(sensors.MizzenHalyard, "lock_2"),
    "mizzen-reef-2-overhoist": LoadField(sensors.MizzenHalyard, "overhoist_2"),
    "mizzen-runner-ps-rel-position": LoadField(
        sensors.MizzenRunnerCaptivePS, "relative_position"
    ),
    #'mizzen-runner-ps-load': #where's the loadpin?
    "mizzen-runner-sb-rel-position": LoadField(
        sensors.MizzenRunnerCaptiveSB, "relative_position"
    ),
    #'mizzen-runner-sb-load': #where's the loadpin?
    "mizzen-sheet-load": LoadField(sensors.MizzenSheetCaptive, "load"),
    "mizzen-sheet-rel-position": LoadField(
        sensors.MizzenSheetCaptive, "relative_position"
    ),
    "mizzen-vang-position": LoadField(sensors.MizzenVang, "position"),
    # "mizzen-vang-load": LoadField(sensors.MizzenVang, "load"), #bottom or rod?
    "staysail-sheet-feeder-ps-load": LoadField(sensors.StaysailSheetFeederPs, "load"),
    "staysail-sheet-feeder-sb-load": LoadField(sensors.StaysailSheetFeederSb, "load"),
    "staysail-sheet-ps-load": LoadField(sensors.StaysailSheetCaptivePS, "load"),
    "staysail-sheet-ps-rel-position": LoadField(
        sensors.StaysailSheetCaptivePS, "relative_position"
    ),
    "staysail-sheet-sb-load": LoadField(sensors.StaysailSheetCaptiveSB, "load"),
    "staysail-sheet-sb-rel-position": LoadField(
        sensors.StaysailSheetCaptiveSB, "relative_position"
    ),
    "staysail-stay-adjuster-load": LoadField(sensors.StaysailStayAdjuster, "load"),
    "staysail-stay-adjuster-position": LoadField(
        sensors.StaysailStayAdjuster, "position"
    ),
    # TODO: add non-captive winches
}
