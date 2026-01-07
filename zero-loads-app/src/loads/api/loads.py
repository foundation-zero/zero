from typing import Any, Callable, Literal, Protocol

import loads.sensors.sensors as sensors
from loads.sensors import LoadsModel, at

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
    "lock_A3C0",
    "lock_A2",
    "lock_staysail",
    "lock_stormjib",
    "overhoist",
    "overhoist_full",
    "overhoist_1",
    "overhoist_2",
    "overhoist_3",
    "overhoist_A3C0",
    "overhoist_A2",
    "overhoist_staysail",
    "overhoist_stormjib",
    "load_bottom",
    "position_1",
    "position_2",
    "relative_position_1",
    "relative_position_2",
]


class LoadsField[T: LoadsModel](Protocol):
    model: type[T]

    def give(self, data: T) -> Any: ...


class LoadField[T: LoadsModel]:
    def __init__(self, model: type[T], field: Fields) -> None:
        self.model = model
        if field not in self.model.model_fields:
            raise Exception(f"Field {field} not in sensor model {model}")
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
    "blade-adjuster-relative-position": LoadField(
        sensors.BladeAdjuster, "relative_position"
    ),
    "blade-cunningham-load": LoadField(sensors.BladeCunningham, "load"),
    "blade-cunningham-position": LoadField(
        sensors.BladeCunningham, "position_1"
    ),  # TODO: figure out what position 1 and 2 are
    "blade-cunningham-relative-position": LoadField(
        sensors.BladeCunningham, "relative_position_1"
    ),
    "blade-sheet-feeder-ps-load": LoadField(sensors.BladeSheetFeederPs, "load"),
    "blade-sheet-feeder-sb-load": LoadField(sensors.BladeSheetFeederSb, "load"),
    "blade-tweaker-ps-load": LoadField(sensors.BladeTweakerPS, "load"),
    "blade-tweaker-ps-position": LoadField(sensors.BladeTweakerPS, "position"),
    "blade-tweaker-ps-relative-position": LoadField(
        sensors.BladeTweakerPS, "relative_position"
    ),
    "blade-tweaker-sb-load": LoadField(sensors.BladeTweakerSB, "load"),
    "blade-tweaker-sb-position": LoadField(sensors.BladeTweakerSB, "position"),
    "blade-tweaker-sb-relative-position": LoadField(
        sensors.BladeTweakerSB, "relative_position"
    ),
    "code-zero-lock": LoadField(sensors.HeadsailLocks, "lock_A3C0"),
    "code-zero-overhoist": LoadField(sensors.HeadsailLocks, "overhoist_A3C0"),
    "code-zero-tack-load": LoadField(sensors.CodeSailTack, "load"),
    "code-zero-tack-position": LoadField(
        sensors.CodeSailTack, "position_1"
    ),  # TODO: figure out what position 1 and 2 are
    "code-zero-tack-relative-position": LoadField(
        sensors.CodeSailTack, "relative_position_1"
    ),
    "main-boom-reef-1-lock": LoadField(sensors.MainHalyard, "lock_1"),
    "main-boom-reef-2-lock": LoadField(sensors.MainHalyard, "lock_2"),
    "main-boom-reef-3-lock": LoadField(sensors.MainHalyard, "lock_3"),
    "main-checkstay-deflector-ps-load": LoadField(
        sensors.MainCheckstayDeflector, "load_ps"
    ),
    "main-checkstay-deflector-ps-position": LoadField(
        sensors.MainCheckstayDeflector, "position"
    ),  # TODO: Differentiate between ps an sb position
    "main-checkstay-deflector-ps-relative-position": LoadField(
        sensors.MainCheckstayDeflector, "relative_position"
    ),
    "main-checkstay-deflector-sb-load": LoadField(
        sensors.MainCheckstayDeflector, "load_sb"
    ),
    "main-checkstay-deflector-sb-position": LoadField(
        sensors.MainCheckstayDeflector, "position"
    ),  # TODO: Differentiate between ps an sb position
    "main-checkstay-deflector-sb-relative-position": LoadField(
        sensors.MainCheckstayDeflector, "relative_position"
    ),
    "main-checkstay-ps-load": LoadField(sensors.MainCheckstayDeflector, "load_ps"),
    "main-checkstay-sb-load": LoadField(sensors.MainCheckstayDeflector, "load_sb"),
    "main-cunningham-load": LoadField(sensors.MainCunningham, "load"),
    "main-cunningham-position": LoadField(sensors.MainCunningham, "position"),
    "main-cunningham-relative-position": LoadField(
        sensors.MainCunningham, "relative_position"
    ),
    "main-halyard-load": LoadField(sensors.MainHalyard, "load"),
    "main-halyard-lock-full": LoadField(sensors.MainHalyard, "lock_full"),
    "main-halyard-overhoist-full": LoadField(sensors.MainHalyard, "overhoist_full"),
    "main-halyard-reef-1-lock": LoadField(sensors.MainHalyard, "lock_1"),
    "main-halyard-reef-1-overhoist": LoadField(sensors.MainHalyard, "overhoist_1"),
    "main-halyard-reef-2-lock": LoadField(sensors.MainHalyard, "lock_2"),
    "main-halyard-reef-2-overhoist": LoadField(sensors.MainHalyard, "overhoist_2"),
    "main-halyard-reef-3-lock": LoadField(sensors.MainHalyard, "lock_3"),
    "main-halyard-reef-3-overhoist": LoadField(sensors.MainHalyard, "overhoist_3"),
    "main-halyard-relative-position": LoadField(
        sensors.MainHalyard, "relative_position"
    ),
    "main-outhaul-load": LoadField(sensors.MainOuthaul, "load"),
    "main-outhaul-position": LoadField(sensors.MainOuthaul, "position"),
    "main-outhaul-relative-position": LoadField(
        sensors.MainOuthaul, "relative_position"
    ),
    "main-preventer-load": LoadField(sensors.MainPreventer, "load"),
    "main-preventer-position": LoadField(sensors.MainPreventer, "position"),
    "main-preventer-relative-position": LoadField(
        sensors.MainPreventer, "relative_position"
    ),
    "main-runner-captive-ps-relative-position": LoadField(
        sensors.MainRunnerCaptivePS, "relative_position"
    ),
    "main-runner-captive-sb-relative-position": LoadField(
        sensors.MainRunnerCaptiveSB, "relative_position"
    ),
    "main-runner-ps-load": LoadField(sensors.MainRunnerLoadPs, "load"),
    "main-runner-sb-load": LoadField(sensors.MainRunnerLoadSb, "load"),
    #'main-sheet-load': #TODO: Find the loadpin
    "main-traveler-relative-position": LoadField(
        sensors.MainTraveler, "relative_position"
    ),
    "main-vang-load": LoadField(
        sensors.MainVang, "load_bottom"
    ),  # TODO: use bottom or rod?
    "main-vang-position": LoadField(sensors.MainVang, "position"),
    "main-vang-relative-position": LoadField(sensors.MainVang, "relative_position"),
    "mizzen-boom-reef-1-lock": LoadField(sensors.MizzenHalyard, "lock_1"),
    "mizzen-boom-reef-2-lock": LoadField(sensors.MizzenHalyard, "lock_2"),
    "mizzen-checkstay-deflector-ps-load": LoadField(
        sensors.MizzenCheckstayDeflector, "load_ps"
    ),
    "mizzen-checkstay-deflector-ps-position": LoadField(
        sensors.MizzenCheckstayDeflector, "position"
    ),  # TODO: Differentiate between ps an sb position
    "mizzen-checkstay-deflector-ps-relative-position": LoadField(
        sensors.MizzenCheckstayDeflector, "relative_position"
    ),
    "mizzen-checkstay-deflector-sb-load": LoadField(
        sensors.MizzenCheckstayDeflector, "load_sb"
    ),
    "mizzen-checkstay-deflector-sb-position": LoadField(
        sensors.MizzenCheckstayDeflector, "position"
    ),  # TODO: Differentiate between ps an sb position
    "mizzen-checkstay-deflector-sb-relative-position": LoadField(
        sensors.MizzenCheckstayDeflector, "relative_position"
    ),
    "mizzen-checkstay-ps-load": LoadField(sensors.MizzenCheckstayDeflector, "load_ps"),
    "mizzen-checkstay-sb-load": LoadField(sensors.MizzenCheckstayDeflector, "load_sb"),
    "mizzen-cunningham-load": LoadField(sensors.MizzenCunningham, "load"),
    "mizzen-cunningham-position": LoadField(sensors.MizzenCunningham, "position"),
    "mizzen-cunningham-relative-position": LoadField(
        sensors.MizzenCunningham, "relative_position"
    ),
    "mizzen-halyard-load": LoadField(sensors.MizzenHalyard, "load"),
    "mizzen-halyard-position": LoadField(sensors.MizzenHalyard, "position"),
    "mizzen-halyard-relative-position": LoadField(
        sensors.MizzenHalyard, "relative_position"
    ),
    "mizzen-headsail-lock": LoadField(sensors.MizzenHeadsailLocks, "lock"),
    "mizzen-headsail-overhoist": LoadField(sensors.MizzenHeadsailLocks, "overhoist"),
    "mizzen-headsail-tack-adjuster-load": LoadField(
        sensors.MizzenHeadsailTackAdjuster, "load"
    ),
    "mizzen-headsail-tack-adjuster-position": LoadField(
        sensors.MizzenHeadsailTackAdjuster, "position"
    ),
    "mizzen-headsail-tack-adjuster-relative-position": LoadField(
        sensors.MizzenHeadsailTackAdjuster, "relative_position"
    ),
    "mizzen-outhaul-load": LoadField(sensors.MizzenOuthaul, "load"),
    "mizzen-outhaul-position": LoadField(sensors.MizzenOuthaul, "position"),
    "mizzen-outhaul-relative-position": LoadField(
        sensors.MizzenOuthaul, "relative_position"
    ),
    "mizzen-preventer-load": LoadField(sensors.MizzenPreventer, "load"),
    "mizzen-preventer-position": LoadField(sensors.MizzenPreventer, "position"),
    "mizzen-preventer-relative-position": LoadField(
        sensors.MizzenPreventer, "relative_position"
    ),
    "mizzen-reef-1-lock": LoadField(sensors.MizzenHalyard, "lock_1"),
    "mizzen-reef-1-overhoist": LoadField(sensors.MizzenHalyard, "overhoist_1"),
    "mizzen-reef-2-lock": LoadField(sensors.MizzenHalyard, "lock_2"),
    "mizzen-reef-2-overhoist": LoadField(sensors.MizzenHalyard, "overhoist_2"),
    "mizzen-runner-captive-ps-relative-position": LoadField(
        sensors.MizzenRunnerCaptivePS, "relative_position"
    ),
    "mizzen-runner-captive-sb-relative-position": LoadField(
        sensors.MizzenRunnerCaptiveSB, "relative_position"
    ),
    "mizzen-runner-ps-load": LoadField(sensors.MizzenRunnerLoadPs, "load"),
    "mizzen-runner-sb-load": LoadField(sensors.MizzenRunnerLoadSb, "load"),
    "mizzen-sheet-captive-load": LoadField(sensors.MizzenSheetCaptive, "load"),
    "mizzen-sheet-captive-relative-position": LoadField(
        sensors.MizzenSheetCaptive, "relative_position"
    ),
    "mizzen-vang-load": LoadField(
        sensors.MizzenVang, "load_bottom"
    ),  # TODO: use bottom or rod?
    "mizzen-vang-position": LoadField(sensors.MizzenVang, "position"),
    "mizzen-vang-relative-position": LoadField(sensors.MizzenVang, "relative_position"),
    "staysail-lock": LoadField(sensors.HeadsailLocks, "lock_staysail"),
    "staysail-overhoist": LoadField(sensors.HeadsailLocks, "overhoist_staysail"),
    "staysail-sheet-captive-ps-load": LoadField(sensors.StaysailSheetCaptivePS, "load"),
    "staysail-sheet-captive-ps-relative-position": LoadField(
        sensors.StaysailSheetCaptivePS, "relative_position"
    ),
    "staysail-sheet-captive-sb-load": LoadField(sensors.StaysailSheetCaptiveSB, "load"),
    "staysail-sheet-captive-sb-relative-position": LoadField(
        sensors.StaysailSheetCaptiveSB, "relative_position"
    ),
    "staysail-sheet-feeder-ps-load": LoadField(sensors.StaysailSheetFeederPs, "load"),
    "staysail-sheet-feeder-sb-load": LoadField(sensors.StaysailSheetFeederSb, "load"),
    "staysail-stay-adjuster-load": LoadField(sensors.StaysailStayAdjuster, "load"),
    "staysail-stay-adjuster-position": LoadField(
        sensors.StaysailStayAdjuster, "position"
    ),
    "staysail-stay-adjuster-relative-position": LoadField(
        sensors.StaysailStayAdjuster, "relative_position"
    ),
    "storm-jib-lock": LoadField(sensors.HeadsailLocks, "lock_stormjib"),
    "storm-jib-overhoist": LoadField(sensors.HeadsailLocks, "overhoist_stormjib"),
    "test-at-latitude": LoadField(at.SystemLatitude, "load"),
    "test-at-longitude": LoadField(at.SystemLongitude, "load"),
    "test-at-utcdate": LoadField(at.UTCDate, "load"),
}
