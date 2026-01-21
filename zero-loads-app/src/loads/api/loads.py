from typing import Any, Callable, Literal, Protocol

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
    "load_deflector",
    "alarm",
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
    "blade-adjuster-alarm": LoadField(sail_system.BladeAdjuster, "alarm"),
    "blade-cunningham-load": LoadField(sail_system.BladeCunningham, "load"),
    "blade-cunningham-position": LoadField(
        sail_system.BladeCunningham, "position_1"
    ),  # TODO: position 1 and position 2 should be more or less equal. TBD how to deal with this.
    "blade-cunningham-relative-position": LoadField(
        sail_system.BladeCunningham,
        "relative_position_1",
    ),  # TODO: position 1 and position 2 should be more or less equal. TBD how to deal with this.
    "blade-cunningham-alarm": LoadField(sail_system.BladeCunningham, "alarm"),
    "blade-sheet-feeder-ps-load": LoadField(sail_system.BladeSheetFeederPs, "load"),
    "blade-sheet-feeder-ps-alarm": LoadField(sail_system.BladeSheetFeederPs, "alarm"),
    "blade-sheet-feeder-sb-load": LoadField(sail_system.BladeSheetFeederSb, "load"),
    "blade-sheet-feeder-sb-alarm": LoadField(sail_system.BladeSheetFeederSb, "alarm"),
    "blade-tweaker-ps-load": LoadField(sail_system.BladeTweakerPS, "load"),
    "blade-tweaker-ps-position": LoadField(sail_system.BladeTweakerPS, "position"),
    "blade-tweaker-ps-relative-position": LoadField(
        sail_system.BladeTweakerPS, "relative_position"
    ),
    "blade-tweaker-ps-alarm": LoadField(sail_system.BladeTweakerPS, "alarm"),
    "blade-tweaker-sb-load": LoadField(sail_system.BladeTweakerSB, "load"),
    "blade-tweaker-sb-position": LoadField(sail_system.BladeTweakerSB, "position"),
    "blade-tweaker-sb-relative-position": LoadField(
        sail_system.BladeTweakerSB, "relative_position"
    ),
    "blade-tweaker-sb-alarm": LoadField(sail_system.BladeTweakerSB, "alarm"),
    "code-zero-lock": LoadField(sail_system.HeadsailLocks, "lock_A3C0"),
    "code-zero-overhoist": LoadField(sail_system.HeadsailLocks, "overhoist_A3C0"),
    "code-zero-tack-load": LoadField(sail_system.CodeSailTack, "load"),
    "code-zero-tack-position": LoadField(
        sail_system.CodeSailTack, "position_1"
    ),  # TODO: position 1 and position 2 should be more or less equal. TBD how to deal with this.
    "code-zero-tack-relative-position": LoadField(
        sail_system.CodeSailTack,
        "relative_position_1",  # TODO: position 1 and position 2 should be more or less equal. TBD how to deal with this.
    ),
    "code-zero-tack-alarm": LoadField(sail_system.CodeSailTack, "alarm"),
    "main-boom-reef-1-lock": LoadField(sail_system.MainHalyard, "lock_1"),
    "main-boom-reef-2-lock": LoadField(sail_system.MainHalyard, "lock_2"),
    "main-boom-reef-3-lock": LoadField(sail_system.MainHalyard, "lock_3"),
    "main-checkstay-deflector-load": LoadField(
        sail_system.MainCheckstayDeflector, "load_deflector"
    ),
    "main-checkstay-deflector-relative-position": LoadField(
        sail_system.MainCheckstayDeflector, "relative_position"
    ),
    "main-checkstay-ps-load": LoadField(sail_system.MainCheckstayDeflector, "load_ps"),
    "main-checkstay-sb-load": LoadField(sail_system.MainCheckstayDeflector, "load_sb"),
    "main-checkstay-deflector-alarm": LoadField(
        sail_system.MainCheckstayDeflector, "alarm"
    ),
    "main-cunningham-load": LoadField(sail_system.MainCunningham, "load"),
    "main-cunningham-position": LoadField(sail_system.MainCunningham, "position"),
    "main-cunningham-relative-position": LoadField(
        sail_system.MainCunningham, "relative_position"
    ),
    "main-cunningham-alarm": LoadField(sail_system.MainCunningham, "alarm"),
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
    "main-halyard-alarm": LoadField(sail_system.MainHalyard, "alarm"),
    "main-outhaul-load": LoadField(sail_system.MainOuthaul, "load"),
    "main-outhaul-position": LoadField(sail_system.MainOuthaul, "position"),
    "main-outhaul-relative-position": LoadField(
        sail_system.MainOuthaul, "relative_position"
    ),
    "main-outhaul-alarm": LoadField(sail_system.MainOuthaul, "alarm"),
    "main-preventer-load": LoadField(sail_system.MainPreventer, "load"),
    "main-preventer-position": LoadField(sail_system.MainPreventer, "position"),
    "main-preventer-relative-position": LoadField(
        sail_system.MainPreventer, "relative_position"
    ),
    "main-preventer-alarm": LoadField(sail_system.MainPreventer, "alarm"),
    "main-runner-ps-relative-position": LoadField(
        sail_system.MainRunnerPs, "relative_position"
    ),
    "main-runner-sb-relative-position": LoadField(
        sail_system.MainRunnerSb, "relative_position"
    ),
    "main-runner-ps-load": LoadField(sail_system.MainRunnerPs, "load"),
    "main-runner-ps-alarm": LoadField(sail_system.MainRunnerPs, "alarm"),
    "main-runner-sb-load": LoadField(sail_system.MainRunnerSb, "load"),
    "main-runner-sb-alarm": LoadField(sail_system.MainRunnerSb, "alarm"),
    "main-sheet-load": LoadField(sail_system.MainSheet, "load"),
    "main-sheet-position": LoadField(sail_system.MainSheet, "position"),
    "main-sheet-relative-position": LoadField(
        sail_system.MainSheet, "relative_position"
    ),
    "main-sheet-alarm": LoadField(sail_system.MainSheet, "alarm"),
    "main-traveler-relative-position": LoadField(
        sail_system.MainTraveler, "relative_position"
    ),
    "main-vang-load": LoadField(sail_system.MainVang, "load"),
    "main-vang-position": LoadField(sail_system.MainVang, "position"),
    "main-vang-relative-position": LoadField(sail_system.MainVang, "relative_position"),
    "main-vang-alarm": LoadField(sail_system.MainVang, "alarm"),
    "mizzen-boom-reef-1-lock": LoadField(sail_system.MizzenHalyard, "lock_1"),
    "mizzen-boom-reef-2-lock": LoadField(sail_system.MizzenHalyard, "lock_2"),
    "mizzen-checkstay-deflector-load": LoadField(
        sail_system.MizzenCheckstayDeflector, "load_deflector"
    ),
    "mizzen-checkstay-deflector-position": LoadField(
        sail_system.MizzenCheckstayDeflector, "position"
    ),
    "mizzen-checkstay-deflector-relative-position": LoadField(
        sail_system.MizzenCheckstayDeflector, "relative_position"
    ),
    "mizzen-checkstay-ps-load": LoadField(
        sail_system.MizzenCheckstayDeflector, "load_ps"
    ),
    "mizzen-checkstay-sb-load": LoadField(
        sail_system.MizzenCheckstayDeflector, "load_sb"
    ),
    "mizzen-checkstay-deflector-alarm": LoadField(
        sail_system.MizzenCheckstayDeflector, "alarm"
    ),
    "mizzen-cunningham-load": LoadField(sail_system.MizzenCunningham, "load"),
    "mizzen-cunningham-position": LoadField(sail_system.MizzenCunningham, "position"),
    "mizzen-cunningham-relative-position": LoadField(
        sail_system.MizzenCunningham, "relative_position"
    ),
    "mizzen-cunningham-alarm": LoadField(sail_system.MizzenCunningham, "alarm"),
    "mizzen-halyard-load": LoadField(sail_system.MizzenHalyard, "load"),
    "mizzen-halyard-position": LoadField(sail_system.MizzenHalyard, "position"),
    "mizzen-halyard-relative-position": LoadField(
        sail_system.MizzenHalyard, "relative_position"
    ),
    "mizzen-halyard-alarm": LoadField(sail_system.MizzenHalyard, "alarm"),
    "mizzen-jib-lock": LoadField(sail_system.MizzenHeadsailLocks, "lock"),
    "mizzen-jib-overhoist": LoadField(sail_system.MizzenHeadsailLocks, "overhoist"),
    "mizzen-jib-tack-adjuster-load": LoadField(
        sail_system.MizzenHeadsailTackAdjuster, "load"
    ),
    "mizzen-jib-tack-adjuster-position": LoadField(
        sail_system.MizzenHeadsailTackAdjuster, "position"
    ),
    "mizzen-jib-tack-adjuster-relative-position": LoadField(
        sail_system.MizzenHeadsailTackAdjuster, "relative_position"
    ),
    "mizzen-jib-tack-adjuster-alarm": LoadField(
        sail_system.MizzenHeadsailTackAdjuster, "alarm"
    ),
    "mizzen-outhaul-load": LoadField(sail_system.MizzenOuthaul, "load"),
    "mizzen-outhaul-position": LoadField(sail_system.MizzenOuthaul, "position"),
    "mizzen-outhaul-relative-position": LoadField(
        sail_system.MizzenOuthaul, "relative_position"
    ),
    "mizzen-outhaul-alarm": LoadField(sail_system.MizzenOuthaul, "alarm"),
    "mizzen-preventer-load": LoadField(sail_system.MizzenPreventer, "load"),
    "mizzen-preventer-position": LoadField(sail_system.MizzenPreventer, "position"),
    "mizzen-preventer-relative-position": LoadField(
        sail_system.MizzenPreventer, "relative_position"
    ),
    "mizzen-preventer-alarm": LoadField(sail_system.MizzenPreventer, "alarm"),
    "mizzen-reef-1-lock": LoadField(sail_system.MizzenHalyard, "lock_1"),
    "mizzen-reef-1-overhoist": LoadField(sail_system.MizzenHalyard, "overhoist_1"),
    "mizzen-reef-2-lock": LoadField(sail_system.MizzenHalyard, "lock_2"),
    "mizzen-reef-2-overhoist": LoadField(sail_system.MizzenHalyard, "overhoist_2"),
    "mizzen-runner-ps-relative-position": LoadField(
        sail_system.MizzenRunnerPs, "relative_position"
    ),
    "mizzen-runner-sb-relative-position": LoadField(
        sail_system.MizzenRunnerSb, "relative_position"
    ),
    "mizzen-runner-ps-load": LoadField(sail_system.MizzenRunnerPs, "load"),
    "mizzen-runner-ps-alarm": LoadField(sail_system.MizzenRunnerPs, "alarm"),
    "mizzen-runner-sb-load": LoadField(sail_system.MizzenRunnerSb, "load"),
    "mizzen-runner-sb-alarm": LoadField(sail_system.MizzenRunnerSb, "alarm"),
    "mizzen-sheet-load": LoadField(sail_system.MizzenSheet, "load"),
    "mizzen-sheet-relative-position": LoadField(
        sail_system.MizzenSheet, "relative_position"
    ),
    "mizzen-sheet-alarm": LoadField(sail_system.MizzenSheet, "alarm"),
    "mizzen-vang-load": LoadField(sail_system.MizzenVang, "load"),
    "mizzen-vang-position": LoadField(sail_system.MizzenVang, "position"),
    "mizzen-vang-relative-position": LoadField(
        sail_system.MizzenVang, "relative_position"
    ),
    "mizzen-vang-alarm": LoadField(sail_system.MizzenVang, "alarm"),
    "staysail-lock": LoadField(sail_system.HeadsailLocks, "lock_staysail"),
    "staysail-overhoist": LoadField(sail_system.HeadsailLocks, "overhoist_staysail"),
    "staysail-sheet-ps-relative-position": LoadField(
        sail_system.StaysailSheetPs, "relative_position"
    ),
    "staysail-sheet-sb-relative-position": LoadField(
        sail_system.StaysailSheetSb, "relative_position"
    ),
    "staysail-sheet-feeder-ps-load": LoadField(
        sail_system.StaysailSheetFeederPs, "load"
    ),
    "staysail-sheet-feeder-ps-alarm": LoadField(
        sail_system.StaysailSheetFeederPs, "alarm"
    ),
    "staysail-sheet-feeder-sb-load": LoadField(
        sail_system.StaysailSheetFeederSb, "load"
    ),
    "staysail-sheet-feeder-sb-alarm": LoadField(
        sail_system.StaysailSheetFeederSb, "alarm"
    ),
    "staysail-stay-adjuster-load": LoadField(sail_system.StaysailStayAdjuster, "load"),
    "staysail-stay-adjuster-position": LoadField(
        sail_system.StaysailStayAdjuster, "position"
    ),
    "staysail-stay-adjuster-relative-position": LoadField(
        sail_system.StaysailStayAdjuster, "relative_position"
    ),
    "staysail-stay-adjuster-alarm": LoadField(
        sail_system.StaysailStayAdjuster, "alarm"
    ),
    "storm-jib-lock": LoadField(sail_system.HeadsailLocks, "lock_stormjib"),
    "storm-jib-overhoist": LoadField(sail_system.HeadsailLocks, "overhoist_stormjib"),
    "aws": LoadField(at.ApparentWindSpeed, "value"),
    "awa": LoadField(at.ApparentWindAngle, "value"),
}
