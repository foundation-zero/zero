from typing import Any, Callable, Literal, Protocol

from loads.sensors import LoadsModel, at, plc

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
    "blade-adjuster-load": LoadField(plc.BladeAdjuster, "load"),
    "blade-adjuster-position": LoadField(plc.BladeAdjuster, "position"),
    "blade-adjuster-relative-position": LoadField(
        plc.BladeAdjuster, "relative_position"
    ),
    "blade-cunningham-load": LoadField(plc.BladeCunningham, "load"),
    "blade-cunningham-position": LoadField(
        plc.BladeCunningham, "position_1"
    ),  # TODO: figure out what position 1 and 2 are
    "blade-cunningham-relative-position": LoadField(
        plc.BladeCunningham, "relative_position_1"
    ),
    "blade-sheet-feeder-ps-load": LoadField(plc.BladeSheetFeederPs, "load"),
    "blade-sheet-feeder-sb-load": LoadField(plc.BladeSheetFeederSb, "load"),
    "blade-tweaker-ps-load": LoadField(plc.BladeTweakerPS, "load"),
    "blade-tweaker-ps-position": LoadField(plc.BladeTweakerPS, "position"),
    "blade-tweaker-ps-relative-position": LoadField(
        plc.BladeTweakerPS, "relative_position"
    ),
    "blade-tweaker-sb-load": LoadField(plc.BladeTweakerSB, "load"),
    "blade-tweaker-sb-position": LoadField(plc.BladeTweakerSB, "position"),
    "blade-tweaker-sb-relative-position": LoadField(
        plc.BladeTweakerSB, "relative_position"
    ),
    "code-zero-lock": LoadField(plc.HeadsailLocks, "lock_A3C0"),
    "code-zero-overhoist": LoadField(plc.HeadsailLocks, "overhoist_A3C0"),
    "code-zero-tack-load": LoadField(plc.CodeSailTack, "load"),
    "code-zero-tack-position": LoadField(
        plc.CodeSailTack, "position_1"
    ),  # TODO: figure out what position 1 and 2 are
    "code-zero-tack-relative-position": LoadField(
        plc.CodeSailTack, "relative_position_1"
    ),
    "main-boom-reef-1-lock": LoadField(plc.MainHalyard, "lock_1"),
    "main-boom-reef-2-lock": LoadField(plc.MainHalyard, "lock_2"),
    "main-boom-reef-3-lock": LoadField(plc.MainHalyard, "lock_3"),
    "main-checkstay-deflector-ps-load": LoadField(
        plc.MainCheckstayDeflector, "load_ps"
    ),
    "main-checkstay-deflector-ps-position": LoadField(
        plc.MainCheckstayDeflector, "position"
    ),  # TODO: Differentiate between ps an sb position
    "main-checkstay-deflector-ps-relative-position": LoadField(
        plc.MainCheckstayDeflector, "relative_position"
    ),
    "main-checkstay-deflector-sb-load": LoadField(
        plc.MainCheckstayDeflector, "load_sb"
    ),
    "main-checkstay-deflector-sb-position": LoadField(
        plc.MainCheckstayDeflector, "position"
    ),  # TODO: Differentiate between ps an sb position
    "main-checkstay-deflector-sb-relative-position": LoadField(
        plc.MainCheckstayDeflector, "relative_position"
    ),
    "main-checkstay-ps-load": LoadField(plc.MainCheckstayDeflector, "load_ps"),
    "main-checkstay-sb-load": LoadField(plc.MainCheckstayDeflector, "load_sb"),
    "main-cunningham-load": LoadField(plc.MainCunningham, "load"),
    "main-cunningham-position": LoadField(plc.MainCunningham, "position"),
    "main-cunningham-relative-position": LoadField(
        plc.MainCunningham, "relative_position"
    ),
    "main-halyard-load": LoadField(plc.MainHalyard, "load"),
    "main-halyard-lock-full": LoadField(plc.MainHalyard, "lock_full"),
    "main-halyard-overhoist-full": LoadField(
        plc.MainHalyard, "overhoist_full"
    ),
    "main-halyard-reef-1-lock": LoadField(plc.MainHalyard, "lock_1"),
    "main-halyard-reef-1-overhoist": LoadField(plc.MainHalyard, "overhoist_1"),
    "main-halyard-reef-2-lock": LoadField(plc.MainHalyard, "lock_2"),
    "main-halyard-reef-2-overhoist": LoadField(plc.MainHalyard, "overhoist_2"),
    "main-halyard-reef-3-lock": LoadField(plc.MainHalyard, "lock_3"),
    "main-halyard-reef-3-overhoist": LoadField(plc.MainHalyard, "overhoist_3"),
    "main-halyard-relative-position": LoadField(
        plc.MainHalyard, "relative_position"
    ),
    "main-outhaul-load": LoadField(plc.MainOuthaul, "load"),
    "main-outhaul-position": LoadField(plc.MainOuthaul, "position"),
    "main-outhaul-relative-position": LoadField(
        plc.MainOuthaul, "relative_position"
    ),
    "main-preventer-load": LoadField(plc.MainPreventer, "load"),
    "main-preventer-position": LoadField(plc.MainPreventer, "position"),
    "main-preventer-relative-position": LoadField(
        plc.MainPreventer, "relative_position"
    ),
    "main-runner-captive-ps-relative-position": LoadField(
        plc.MainRunnerCaptivePS, "relative_position"
    ),
    "main-runner-captive-sb-relative-position": LoadField(
        plc.MainRunnerCaptiveSB, "relative_position"
    ),
    "main-runner-ps-load": LoadField(plc.MainRunnerLoadPs, "load"),
    "main-runner-sb-load": LoadField(plc.MainRunnerLoadSb, "load"),
    #'main-sheet-load': #TODO: Find the loadpin
    "main-traveler-relative-position": LoadField(
        plc.MainTraveler, "relative_position"
    ),
    "main-vang-load": LoadField(
        plc.MainVang, "load_bottom"
    ),  # TODO: use bottom or rod?
    "main-vang-position": LoadField(plc.MainVang, "position"),
    "main-vang-relative-position": LoadField(
        plc.MainVang, "relative_position"
    ),
    "mizzen-boom-reef-1-lock": LoadField(plc.MizzenHalyard, "lock_1"),
    "mizzen-boom-reef-2-lock": LoadField(plc.MizzenHalyard, "lock_2"),
    "mizzen-checkstay-deflector-ps-load": LoadField(
        plc.MizzenCheckstayDeflector, "load_ps"
    ),
    "mizzen-checkstay-deflector-ps-position": LoadField(
        plc.MizzenCheckstayDeflector, "position"
    ),  # TODO: Differentiate between ps an sb position
    "mizzen-checkstay-deflector-ps-relative-position": LoadField(
        plc.MizzenCheckstayDeflector, "relative_position"
    ),
    "mizzen-checkstay-deflector-sb-load": LoadField(
        plc.MizzenCheckstayDeflector, "load_sb"
    ),
    "mizzen-checkstay-deflector-sb-position": LoadField(
        plc.MizzenCheckstayDeflector, "position"
    ),  # TODO: Differentiate between ps an sb position
    "mizzen-checkstay-deflector-sb-relative-position": LoadField(
        plc.MizzenCheckstayDeflector, "relative_position"
    ),
    "mizzen-checkstay-ps-load": LoadField(
        plc.MizzenCheckstayDeflector, "load_ps"
    ),
    "mizzen-checkstay-sb-load": LoadField(
        plc.MizzenCheckstayDeflector, "load_sb"
    ),
    "mizzen-cunningham-load": LoadField(plc.MizzenCunningham, "load"),
    "mizzen-cunningham-position": LoadField(plc.MizzenCunningham, "position"),
    "mizzen-cunningham-relative-position": LoadField(
        plc.MizzenCunningham, "relative_position"
    ),
    "mizzen-halyard-load": LoadField(plc.MizzenHalyard, "load"),
    "mizzen-halyard-position": LoadField(plc.MizzenHalyard, "position"),
    "mizzen-halyard-relative-position": LoadField(
        plc.MizzenHalyard, "relative_position"
    ),
    "mizzen-headsail-lock": LoadField(plc.MizzenHeadsailLocks, "lock"),
    "mizzen-headsail-overhoist": LoadField(
        plc.MizzenHeadsailLocks, "overhoist"
    ),
    "mizzen-headsail-tack-adjuster-load": LoadField(
        plc.MizzenHeadsailTackAdjuster, "load"
    ),
    "mizzen-headsail-tack-adjuster-position": LoadField(
        plc.MizzenHeadsailTackAdjuster, "position"
    ),
    "mizzen-headsail-tack-adjuster-relative-position": LoadField(
        plc.MizzenHeadsailTackAdjuster, "relative_position"
    ),
    "mizzen-outhaul-load": LoadField(plc.MizzenOuthaul, "load"),
    "mizzen-outhaul-position": LoadField(plc.MizzenOuthaul, "position"),
    "mizzen-outhaul-relative-position": LoadField(
        plc.MizzenOuthaul, "relative_position"
    ),
    "mizzen-preventer-load": LoadField(plc.MizzenPreventer, "load"),
    "mizzen-preventer-position": LoadField(plc.MizzenPreventer, "position"),
    "mizzen-preventer-relative-position": LoadField(
        plc.MizzenPreventer, "relative_position"
    ),
    "mizzen-reef-1-lock": LoadField(plc.MizzenHalyard, "lock_1"),
    "mizzen-reef-1-overhoist": LoadField(plc.MizzenHalyard, "overhoist_1"),
    "mizzen-reef-2-lock": LoadField(plc.MizzenHalyard, "lock_2"),
    "mizzen-reef-2-overhoist": LoadField(plc.MizzenHalyard, "overhoist_2"),
    "mizzen-runner-captive-ps-relative-position": LoadField(
        plc.MizzenRunnerCaptivePS, "relative_position"
    ),
    "mizzen-runner-captive-sb-relative-position": LoadField(
        plc.MizzenRunnerCaptiveSB, "relative_position"
    ),
    "mizzen-runner-ps-load": LoadField(plc.MizzenRunnerLoadPs, "load"),
    "mizzen-runner-sb-load": LoadField(plc.MizzenRunnerLoadSb, "load"),
    "mizzen-sheet-captive-load": LoadField(plc.MizzenSheetCaptive, "load"),
    "mizzen-sheet-captive-relative-position": LoadField(
        plc.MizzenSheetCaptive, "relative_position"
    ),
    "mizzen-vang-load": LoadField(
        plc.MizzenVang, "load_bottom"
    ),  # TODO: use bottom or rod?
    "mizzen-vang-position": LoadField(plc.MizzenVang, "position"),
    "mizzen-vang-relative-position": LoadField(
        plc.MizzenVang, "relative_position"
    ),
    "staysail-lock": LoadField(plc.HeadsailLocks, "lock_staysail"),
    "staysail-overhoist": LoadField(plc.HeadsailLocks, "overhoist_staysail"),
    "staysail-sheet-captive-ps-load": LoadField(
        plc.StaysailSheetCaptivePS, "load"
    ),
    "staysail-sheet-captive-ps-relative-position": LoadField(
        plc.StaysailSheetCaptivePS, "relative_position"
    ),
    "staysail-sheet-captive-sb-load": LoadField(
        plc.StaysailSheetCaptiveSB, "load"
    ),
    "staysail-sheet-captive-sb-relative-position": LoadField(
        plc.StaysailSheetCaptiveSB, "relative_position"
    ),
    "staysail-sheet-feeder-ps-load": LoadField(
        plc.StaysailSheetFeederPs, "load"
    ),
    "staysail-sheet-feeder-sb-load": LoadField(
        plc.StaysailSheetFeederSb, "load"
    ),
    "staysail-stay-adjuster-load": LoadField(plc.StaysailStayAdjuster, "load"),
    "staysail-stay-adjuster-position": LoadField(
        plc.StaysailStayAdjuster, "position"
    ),
    "staysail-stay-adjuster-relative-position": LoadField(
        plc.StaysailStayAdjuster, "relative_position"
    ),
    "storm-jib-lock": LoadField(plc.HeadsailLocks, "lock_stormjib"),
    "storm-jib-overhoist": LoadField(plc.HeadsailLocks, "overhoist_stormjib"),
    "aws": LoadField(at.ApparentWindSpeed, "value"),
    "awa": LoadField(at.ApparentWindAngle, "value"),
}
