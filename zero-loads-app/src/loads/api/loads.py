from typing import Any, Callable, Literal, Protocol

from loads.sensors import LoadsModel, at, sails

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
    "blade-adjuster-load": LoadField(sails.BladeAdjuster, "load"),
    "blade-adjuster-position": LoadField(sails.BladeAdjuster, "position"),
    "blade-adjuster-relative-position": LoadField(
        sails.BladeAdjuster, "relative_position"
    ),
    "blade-cunningham-load": LoadField(sails.BladeCunningham, "load"),
    "blade-cunningham-position": LoadField(
        sails.BladeCunningham, "position_1"
    ),  # TODO: figure out what position 1 and 2 are
    "blade-cunningham-relative-position": LoadField(
        sails.BladeCunningham, "relative_position_1"
    ),
    "blade-sheet-feeder-ps-load": LoadField(sails.BladeSheetFeederPs, "load"),
    "blade-sheet-feeder-sb-load": LoadField(sails.BladeSheetFeederSb, "load"),
    "blade-tweaker-ps-load": LoadField(sails.BladeTweakerPS, "load"),
    "blade-tweaker-ps-position": LoadField(sails.BladeTweakerPS, "position"),
    "blade-tweaker-ps-relative-position": LoadField(
        sails.BladeTweakerPS, "relative_position"
    ),
    "blade-tweaker-sb-load": LoadField(sails.BladeTweakerSB, "load"),
    "blade-tweaker-sb-position": LoadField(sails.BladeTweakerSB, "position"),
    "blade-tweaker-sb-relative-position": LoadField(
        sails.BladeTweakerSB, "relative_position"
    ),
    "code-zero-lock": LoadField(sails.HeadsailLocks, "lock_A3C0"),
    "code-zero-overhoist": LoadField(sails.HeadsailLocks, "overhoist_A3C0"),
    "code-zero-tack-load": LoadField(sails.CodeSailTack, "load"),
    "code-zero-tack-position": LoadField(
        sails.CodeSailTack, "position_1"
    ),  # TODO: figure out what position 1 and 2 are
    "code-zero-tack-relative-position": LoadField(
        sails.CodeSailTack, "relative_position_1"
    ),
    "main-boom-reef-1-lock": LoadField(sails.MainHalyard, "lock_1"),
    "main-boom-reef-2-lock": LoadField(sails.MainHalyard, "lock_2"),
    "main-boom-reef-3-lock": LoadField(sails.MainHalyard, "lock_3"),
    "main-checkstay-deflector-ps-load": LoadField(
        sails.MainCheckstayDeflector, "load_ps"
    ),
    "main-checkstay-deflector-ps-position": LoadField(
        sails.MainCheckstayDeflector, "position"
    ),  # TODO: Differentiate between ps an sb position
    "main-checkstay-deflector-ps-relative-position": LoadField(
        sails.MainCheckstayDeflector, "relative_position"
    ),
    "main-checkstay-deflector-sb-load": LoadField(
        sails.MainCheckstayDeflector, "load_sb"
    ),
    "main-checkstay-deflector-sb-position": LoadField(
        sails.MainCheckstayDeflector, "position"
    ),  # TODO: Differentiate between ps an sb position
    "main-checkstay-deflector-sb-relative-position": LoadField(
        sails.MainCheckstayDeflector, "relative_position"
    ),
    "main-checkstay-ps-load": LoadField(sails.MainCheckstayDeflector, "load_ps"),
    "main-checkstay-sb-load": LoadField(sails.MainCheckstayDeflector, "load_sb"),
    "main-cunningham-load": LoadField(sails.MainCunningham, "load"),
    "main-cunningham-position": LoadField(sails.MainCunningham, "position"),
    "main-cunningham-relative-position": LoadField(
        sails.MainCunningham, "relative_position"
    ),
    "main-halyard-load": LoadField(sails.MainHalyard, "load"),
    "main-halyard-lock-full": LoadField(sails.MainHalyard, "lock_full"),
    "main-halyard-overhoist-full": LoadField(sails.MainHalyard, "overhoist_full"),
    "main-halyard-reef-1-lock": LoadField(sails.MainHalyard, "lock_1"),
    "main-halyard-reef-1-overhoist": LoadField(sails.MainHalyard, "overhoist_1"),
    "main-halyard-reef-2-lock": LoadField(sails.MainHalyard, "lock_2"),
    "main-halyard-reef-2-overhoist": LoadField(sails.MainHalyard, "overhoist_2"),
    "main-halyard-reef-3-lock": LoadField(sails.MainHalyard, "lock_3"),
    "main-halyard-reef-3-overhoist": LoadField(sails.MainHalyard, "overhoist_3"),
    "main-halyard-relative-position": LoadField(
        sails.MainHalyard, "relative_position"
    ),
    "main-outhaul-load": LoadField(sails.MainOuthaul, "load"),
    "main-outhaul-position": LoadField(sails.MainOuthaul, "position"),
    "main-outhaul-relative-position": LoadField(
        sails.MainOuthaul, "relative_position"
    ),
    "main-preventer-load": LoadField(sails.MainPreventer, "load"),
    "main-preventer-position": LoadField(sails.MainPreventer, "position"),
    "main-preventer-relative-position": LoadField(
        sails.MainPreventer, "relative_position"
    ),
    "main-runner-captive-ps-relative-position": LoadField(
        sails.MainRunnerCaptivePS, "relative_position"
    ),
    "main-runner-captive-sb-relative-position": LoadField(
        sails.MainRunnerCaptiveSB, "relative_position"
    ),
    "main-runner-ps-load": LoadField(sails.MainRunnerLoadPs, "load"),
    "main-runner-sb-load": LoadField(sails.MainRunnerLoadSb, "load"),
    #'main-sheet-load': #TODO: Find the loadpin
    "main-traveler-relative-position": LoadField(
        sails.MainTraveler, "relative_position"
    ),
    "main-vang-load": LoadField(
        sails.MainVang, "load_bottom"
    ),  # TODO: use bottom or rod?
    "main-vang-position": LoadField(sails.MainVang, "position"),
    "main-vang-relative-position": LoadField(sails.MainVang, "relative_position"),
    "mizzen-boom-reef-1-lock": LoadField(sails.MizzenHalyard, "lock_1"),
    "mizzen-boom-reef-2-lock": LoadField(sails.MizzenHalyard, "lock_2"),
    "mizzen-checkstay-deflector-ps-load": LoadField(
        sails.MizzenCheckstayDeflector, "load_ps"
    ),
    "mizzen-checkstay-deflector-ps-position": LoadField(
        sails.MizzenCheckstayDeflector, "position"
    ),  # TODO: Differentiate between ps an sb position
    "mizzen-checkstay-deflector-ps-relative-position": LoadField(
        sails.MizzenCheckstayDeflector, "relative_position"
    ),
    "mizzen-checkstay-deflector-sb-load": LoadField(
        sails.MizzenCheckstayDeflector, "load_sb"
    ),
    "mizzen-checkstay-deflector-sb-position": LoadField(
        sails.MizzenCheckstayDeflector, "position"
    ),  # TODO: Differentiate between ps an sb position
    "mizzen-checkstay-deflector-sb-relative-position": LoadField(
        sails.MizzenCheckstayDeflector, "relative_position"
    ),
    "mizzen-checkstay-ps-load": LoadField(sails.MizzenCheckstayDeflector, "load_ps"),
    "mizzen-checkstay-sb-load": LoadField(sails.MizzenCheckstayDeflector, "load_sb"),
    "mizzen-cunningham-load": LoadField(sails.MizzenCunningham, "load"),
    "mizzen-cunningham-position": LoadField(sails.MizzenCunningham, "position"),
    "mizzen-cunningham-relative-position": LoadField(
        sails.MizzenCunningham, "relative_position"
    ),
    "mizzen-halyard-load": LoadField(sails.MizzenHalyard, "load"),
    "mizzen-halyard-position": LoadField(sails.MizzenHalyard, "position"),
    "mizzen-halyard-relative-position": LoadField(
        sails.MizzenHalyard, "relative_position"
    ),
    "mizzen-headsail-lock": LoadField(sails.MizzenHeadsailLocks, "lock"),
    "mizzen-headsail-overhoist": LoadField(sails.MizzenHeadsailLocks, "overhoist"),
    "mizzen-headsail-tack-adjuster-load": LoadField(
        sails.MizzenHeadsailTackAdjuster, "load"
    ),
    "mizzen-headsail-tack-adjuster-position": LoadField(
        sails.MizzenHeadsailTackAdjuster, "position"
    ),
    "mizzen-headsail-tack-adjuster-relative-position": LoadField(
        sails.MizzenHeadsailTackAdjuster, "relative_position"
    ),
    "mizzen-outhaul-load": LoadField(sails.MizzenOuthaul, "load"),
    "mizzen-outhaul-position": LoadField(sails.MizzenOuthaul, "position"),
    "mizzen-outhaul-relative-position": LoadField(
        sails.MizzenOuthaul, "relative_position"
    ),
    "mizzen-preventer-load": LoadField(sails.MizzenPreventer, "load"),
    "mizzen-preventer-position": LoadField(sails.MizzenPreventer, "position"),
    "mizzen-preventer-relative-position": LoadField(
        sails.MizzenPreventer, "relative_position"
    ),
    "mizzen-reef-1-lock": LoadField(sails.MizzenHalyard, "lock_1"),
    "mizzen-reef-1-overhoist": LoadField(sails.MizzenHalyard, "overhoist_1"),
    "mizzen-reef-2-lock": LoadField(sails.MizzenHalyard, "lock_2"),
    "mizzen-reef-2-overhoist": LoadField(sails.MizzenHalyard, "overhoist_2"),
    "mizzen-runner-captive-ps-relative-position": LoadField(
        sails.MizzenRunnerCaptivePS, "relative_position"
    ),
    "mizzen-runner-captive-sb-relative-position": LoadField(
        sails.MizzenRunnerCaptiveSB, "relative_position"
    ),
    "mizzen-runner-ps-load": LoadField(sails.MizzenRunnerLoadPs, "load"),
    "mizzen-runner-sb-load": LoadField(sails.MizzenRunnerLoadSb, "load"),
    "mizzen-sheet-captive-load": LoadField(sails.MizzenSheetCaptive, "load"),
    "mizzen-sheet-captive-relative-position": LoadField(
        sails.MizzenSheetCaptive, "relative_position"
    ),
    "mizzen-vang-load": LoadField(
        sails.MizzenVang, "load_bottom"
    ),  # TODO: use bottom or rod?
    "mizzen-vang-position": LoadField(sails.MizzenVang, "position"),
    "mizzen-vang-relative-position": LoadField(sails.MizzenVang, "relative_position"),
    "staysail-lock": LoadField(sails.HeadsailLocks, "lock_staysail"),
    "staysail-overhoist": LoadField(sails.HeadsailLocks, "overhoist_staysail"),
    "staysail-sheet-captive-ps-load": LoadField(sails.StaysailSheetCaptivePS, "load"),
    "staysail-sheet-captive-ps-relative-position": LoadField(
        sails.StaysailSheetCaptivePS, "relative_position"
    ),
    "staysail-sheet-captive-sb-load": LoadField(sails.StaysailSheetCaptiveSB, "load"),
    "staysail-sheet-captive-sb-relative-position": LoadField(
        sails.StaysailSheetCaptiveSB, "relative_position"
    ),
    "staysail-sheet-feeder-ps-load": LoadField(sails.StaysailSheetFeederPs, "load"),
    "staysail-sheet-feeder-sb-load": LoadField(sails.StaysailSheetFeederSb, "load"),
    "staysail-stay-adjuster-load": LoadField(sails.StaysailStayAdjuster, "load"),
    "staysail-stay-adjuster-position": LoadField(
        sails.StaysailStayAdjuster, "position"
    ),
    "staysail-stay-adjuster-relative-position": LoadField(
        sails.StaysailStayAdjuster, "relative_position"
    ),
    "storm-jib-lock": LoadField(sails.HeadsailLocks, "lock_stormjib"),
    "storm-jib-overhoist": LoadField(sails.HeadsailLocks, "overhoist_stormjib"),
    "aws": LoadField(at.ApparentWindSpeed, "value"),
    "awa": LoadField(at.ApparentWindAngle, "value"),
}
