from typing import Any, Callable, Literal, Protocol

from loads.sensors import LoadsModel, at, sail_system
from loads.sensors import LoadsModel, at, sail_system

Fields = Literal[
    "value",
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
    "blade-adjuster-load": LoadField(sail_system.BladeAdjuster, "load"),
    "blade-adjuster-position": LoadField(sail_system.BladeAdjuster, "position"),
    "blade-adjuster-relative-position": LoadField(
        sail_system.BladeAdjuster, "relative_position"
    ),
    "blade-cunningham-load": LoadField(sail_system.BladeCunningham, "load"),
    "blade-cunningham-position": LoadField(
        sail_system.BladeCunningham, "position_1"
    ),  # TODO: figure out what position 1 and 2 are
    "blade-cunningham-relative-position": LoadField(
        sail_system.BladeCunningham, "relative_position_1"
    ),
    "blade-sheet-feeder-ps-load": LoadField(sail_system.BladeSheetFeederPs, "load"),
    "blade-sheet-feeder-sb-load": LoadField(sail_system.BladeSheetFeederSb, "load"),
    "blade-tweaker-ps-load": LoadField(sail_system.BladeTweakerPS, "load"),
    "blade-tweaker-ps-position": LoadField(sail_system.BladeTweakerPS, "position"),
    "blade-tweaker-ps-relative-position": LoadField(
        sail_system.BladeTweakerPS, "relative_position"
    ),
    "blade-tweaker-sb-load": LoadField(sail_system.BladeTweakerSB, "load"),
    "blade-tweaker-sb-position": LoadField(sail_system.BladeTweakerSB, "position"),
    "blade-tweaker-sb-relative-position": LoadField(
        sail_system.BladeTweakerSB, "relative_position"
    ),
    "code-zero-lock": LoadField(sail_system.HeadsailLocks, "lock_A3C0"),
    "code-zero-overhoist": LoadField(sail_system.HeadsailLocks, "overhoist_A3C0"),
    "code-zero-tack-load": LoadField(sail_system.CodeSailTack, "load"),
    "code-zero-tack-position": LoadField(
        sail_system.CodeSailTack, "position_1"
    ),  # TODO: figure out what position 1 and 2 are
    "code-zero-tack-relative-position": LoadField(
        sail_system.CodeSailTack, "relative_position_1"
    ),
    "main-boom-reef-1-lock": LoadField(sail_system.MainHalyard, "lock_1"),
    "main-boom-reef-2-lock": LoadField(sail_system.MainHalyard, "lock_2"),
    "main-boom-reef-3-lock": LoadField(sail_system.MainHalyard, "lock_3"),
    "main-checkstay-deflector-ps-load": LoadField(
        sail_system.MainCheckstayDeflector, "load_ps"
    ),
    "main-checkstay-deflector-ps-position": LoadField(
        sail_system.MainCheckstayDeflector, "position"
    ),  # TODO: Differentiate between ps an sb position
    "main-checkstay-deflector-ps-relative-position": LoadField(
        sail_system.MainCheckstayDeflector, "relative_position"
    ),
    "main-checkstay-deflector-sb-load": LoadField(
        sail_system.MainCheckstayDeflector, "load_sb"
    ),
    "main-checkstay-deflector-sb-position": LoadField(
        sail_system.MainCheckstayDeflector, "position"
    ),  # TODO: Differentiate between ps an sb position
    "main-checkstay-deflector-sb-relative-position": LoadField(
        sail_system.MainCheckstayDeflector, "relative_position"
    ),
    "main-checkstay-ps-load": LoadField(sail_system.MainCheckstayDeflector, "load_ps"),
    "main-checkstay-sb-load": LoadField(sail_system.MainCheckstayDeflector, "load_sb"),
    "main-cunningham-load": LoadField(sail_system.MainCunningham, "load"),
    "main-cunningham-position": LoadField(sail_system.MainCunningham, "position"),
    "main-cunningham-relative-position": LoadField(
        sail_system.MainCunningham, "relative_position"
    ),
    "main-halyard-load": LoadField(sail_system.MainHalyard, "load"),
    "main-halyard-lock-full": LoadField(sail_system.MainHalyard, "lock_full"),
    "main-halyard-overhoist-full": LoadField(sail_system.MainHalyard, "overhoist_full"),
    "main-halyard-reef-1-lock": LoadField(sail_system.MainHalyard, "lock_1"),
    "main-halyard-reef-1-overhoist": LoadField(sail_system.MainHalyard, "overhoist_1"),
    "main-halyard-reef-2-lock": LoadField(sail_system.MainHalyard, "lock_2"),
    "main-halyard-reef-2-overhoist": LoadField(sail_system.MainHalyard, "overhoist_2"),
    "main-halyard-reef-3-lock": LoadField(sail_system.MainHalyard, "lock_3"),
    "main-halyard-reef-3-overhoist": LoadField(sail_system.MainHalyard, "overhoist_3"),
    "main-halyard-relative-position": LoadField(
        sail_system.MainHalyard, "relative_position"
    ),
    "main-outhaul-load": LoadField(sail_system.MainOuthaul, "load"),
    "main-outhaul-position": LoadField(sail_system.MainOuthaul, "position"),
    "main-outhaul-relative-position": LoadField(
        sail_system.MainOuthaul, "relative_position"
    ),
    "main-preventer-load": LoadField(sail_system.MainPreventer, "load"),
    "main-preventer-position": LoadField(sail_system.MainPreventer, "position"),
    "main-preventer-relative-position": LoadField(
        sail_system.MainPreventer, "relative_position"
    ),
    "main-runner-captive-ps-relative-position": LoadField(
        sail_system.MainRunnerCaptivePS, "relative_position"
    ),
    "main-runner-captive-sb-relative-position": LoadField(
        sail_system.MainRunnerCaptiveSB, "relative_position"
    ),
    "main-runner-ps-load": LoadField(sail_system.MainRunnerLoadPs, "load"),
    "main-runner-sb-load": LoadField(sail_system.MainRunnerLoadSb, "load"),
    #'main-sheet-load': #TODO: Find the loadpin
    "main-traveler-relative-position": LoadField(
        sail_system.MainTraveler, "relative_position"
    ),
    "main-vang-load": LoadField(
        sail_system.MainVang, "load_bottom"
    ),  # TODO: use bottom or rod?
    "main-vang-position": LoadField(sail_system.MainVang, "position"),
    "main-vang-relative-position": LoadField(sail_system.MainVang, "relative_position"),
    "mizzen-boom-reef-1-lock": LoadField(sail_system.MizzenHalyard, "lock_1"),
    "mizzen-boom-reef-2-lock": LoadField(sail_system.MizzenHalyard, "lock_2"),
    "mizzen-checkstay-deflector-ps-load": LoadField(
        sail_system.MizzenCheckstayDeflector, "load_ps"
    ),
    "mizzen-checkstay-deflector-ps-position": LoadField(
        sail_system.MizzenCheckstayDeflector, "position"
    ),  # TODO: Differentiate between ps an sb position
    "mizzen-checkstay-deflector-ps-relative-position": LoadField(
        sail_system.MizzenCheckstayDeflector, "relative_position"
    ),
    "mizzen-checkstay-deflector-sb-load": LoadField(
        sail_system.MizzenCheckstayDeflector, "load_sb"
    ),
    "mizzen-checkstay-deflector-sb-position": LoadField(
        sail_system.MizzenCheckstayDeflector, "position"
    ),  # TODO: Differentiate between ps an sb position
    "mizzen-checkstay-deflector-sb-relative-position": LoadField(
        sail_system.MizzenCheckstayDeflector, "relative_position"
    ),
    "mizzen-checkstay-ps-load": LoadField(
        sail_system.MizzenCheckstayDeflector, "load_ps"
    ),
    "mizzen-checkstay-sb-load": LoadField(
        sail_system.MizzenCheckstayDeflector, "load_sb"
    ),
    "mizzen-cunningham-load": LoadField(sail_system.MizzenCunningham, "load"),
    "mizzen-cunningham-position": LoadField(sail_system.MizzenCunningham, "position"),
    "mizzen-cunningham-relative-position": LoadField(
        sail_system.MizzenCunningham, "relative_position"
    ),
    "mizzen-halyard-load": LoadField(sail_system.MizzenHalyard, "load"),
    "mizzen-halyard-position": LoadField(sail_system.MizzenHalyard, "position"),
    "mizzen-halyard-relative-position": LoadField(
        sail_system.MizzenHalyard, "relative_position"
    ),
    "mizzen-headsail-lock": LoadField(sail_system.MizzenHeadsailLocks, "lock"),
    "mizzen-headsail-overhoist": LoadField(
        sail_system.MizzenHeadsailLocks, "overhoist"
    ),
    "mizzen-headsail-tack-adjuster-load": LoadField(
        sail_system.MizzenHeadsailTackAdjuster, "load"
    ),
    "mizzen-headsail-tack-adjuster-position": LoadField(
        sail_system.MizzenHeadsailTackAdjuster, "position"
    ),
    "mizzen-headsail-tack-adjuster-relative-position": LoadField(
        sail_system.MizzenHeadsailTackAdjuster, "relative_position"
    ),
    "mizzen-outhaul-load": LoadField(sail_system.MizzenOuthaul, "load"),
    "mizzen-outhaul-position": LoadField(sail_system.MizzenOuthaul, "position"),
    "mizzen-outhaul-relative-position": LoadField(
        sail_system.MizzenOuthaul, "relative_position"
    ),
    "mizzen-preventer-load": LoadField(sail_system.MizzenPreventer, "load"),
    "mizzen-preventer-position": LoadField(sail_system.MizzenPreventer, "position"),
    "mizzen-preventer-relative-position": LoadField(
        sail_system.MizzenPreventer, "relative_position"
    ),
    "mizzen-reef-1-lock": LoadField(sail_system.MizzenHalyard, "lock_1"),
    "mizzen-reef-1-overhoist": LoadField(sail_system.MizzenHalyard, "overhoist_1"),
    "mizzen-reef-2-lock": LoadField(sail_system.MizzenHalyard, "lock_2"),
    "mizzen-reef-2-overhoist": LoadField(sail_system.MizzenHalyard, "overhoist_2"),
    "mizzen-runner-captive-ps-relative-position": LoadField(
        sail_system.MizzenRunnerCaptivePS, "relative_position"
    ),
    "mizzen-runner-captive-sb-relative-position": LoadField(
        sail_system.MizzenRunnerCaptiveSB, "relative_position"
    ),
    "mizzen-runner-ps-load": LoadField(sail_system.MizzenRunnerLoadPs, "load"),
    "mizzen-runner-sb-load": LoadField(sail_system.MizzenRunnerLoadSb, "load"),
    "mizzen-sheet-captive-load": LoadField(sail_system.MizzenSheetCaptive, "load"),
    "mizzen-sheet-captive-relative-position": LoadField(
        sail_system.MizzenSheetCaptive, "relative_position"
    ),
    "mizzen-vang-load": LoadField(
        sail_system.MizzenVang, "load_bottom"
    ),  # TODO: use bottom or rod?
    "mizzen-vang-position": LoadField(sail_system.MizzenVang, "position"),
    "mizzen-vang-relative-position": LoadField(
        sail_system.MizzenVang, "relative_position"
    ),
    "staysail-lock": LoadField(sail_system.HeadsailLocks, "lock_staysail"),
    "staysail-overhoist": LoadField(sail_system.HeadsailLocks, "overhoist_staysail"),
    "staysail-sheet-captive-ps-load": LoadField(
        sail_system.StaysailSheetCaptivePS, "load"
    ),
    "staysail-sheet-captive-ps-relative-position": LoadField(
        sail_system.StaysailSheetCaptivePS, "relative_position"
    ),
    "staysail-sheet-captive-sb-load": LoadField(
        sail_system.StaysailSheetCaptiveSB, "load"
    ),
    "staysail-sheet-captive-sb-relative-position": LoadField(
        sail_system.StaysailSheetCaptiveSB, "relative_position"
    ),
    "staysail-sheet-feeder-ps-load": LoadField(
        sail_system.StaysailSheetFeederPs, "load"
    ),
    "staysail-sheet-feeder-sb-load": LoadField(
        sail_system.StaysailSheetFeederSb, "load"
    ),
    "staysail-stay-adjuster-load": LoadField(sail_system.StaysailStayAdjuster, "load"),
    "staysail-stay-adjuster-position": LoadField(
        sail_system.StaysailStayAdjuster, "position"
    ),
    "staysail-stay-adjuster-relative-position": LoadField(
        sail_system.StaysailStayAdjuster, "relative_position"
    ),
    "storm-jib-lock": LoadField(sail_system.HeadsailLocks, "lock_stormjib"),
    "storm-jib-overhoist": LoadField(sail_system.HeadsailLocks, "overhoist_stormjib"),
    "aws": LoadField(at.ApparentWindSpeed, "value"),
    "awa": LoadField(at.ApparentWindAngle, "value"),
}
