import { SailId } from "./consts.sails";
import { VariableId } from "./consts.variables";

export type Dashboard = {
  sail: SailId;
  groups: VariableGroup[];
};

export type VariableGroup = {
  name: string;
  variables: VariableId[];
};

export const group = (name: string, ...variables: VariableId[]): VariableGroup => ({
  name,
  variables,
});

const dashboard = (sail: SailId, ...groups: VariableGroup[]): Dashboard => ({
  sail,
  groups,
});

export const OVERVIEW = dashboard(
  SailId.None,
  group(
    "Main",
    "main-sheet-load",
    "main-traveler-relative-position",
    "main-preventer-load",
    "main-vang-load",
  ),
  group(
    "Main foresails",
    "blade-sheet-feeder-ps-load",
    "blade-sheet-feeder-sb-load",
    "staysail-sheet-feeder-ps-load",
    "staysail-sheet-feeder-sb-load",
  ),
  group("Mizzen", "mizzen-sheet-load", "mizzen-preventer-load", "mizzen-vang-load"),
  group("Mizzen foresails"),
  group(
    "Main Rig",
    "main-runner-ps-load",
    "main-runner-sb-load",
    "main-checkstay-ps-load",
    "main-checkstay-sb-load",
  ),
  group(
    "Mizzen Rig",
    "mizzen-runner-ps-load",
    "mizzen-runner-sb-load",
    "mizzen-checkstay-ps-load",
    "mizzen-checkstay-sb-load",
  ),
  group(
    "Locks",
    "main-halyard-reef-1-lock",
    "main-halyard-reef-2-lock",
    "main-halyard-reef-3-lock",
  ),
);

export const MAIN = dashboard(
  SailId.FullMain,
  group(
    "Main sail",
    "main-sheet-load",
    "main-traveler-relative-position",
    "main-preventer-load",
    "main-vang-load",
  ),
  group("Halyard & trim", "main-halyard-load", "main-cunningham-load"),
  group("Locks", "main-halyard-lock-full"),
  group("Runners", "main-runner-ps-load", "main-runner-sb-load"),
  group("Checkstay", "main-checkstay-ps-load", "main-checkstay-sb-load"),
);

export const MAIN_REEF_1 = dashboard(
  SailId.MainReef1,
  group(
    "Main sail",
    "main-sheet-load",
    "main-traveler-relative-position",
    "main-preventer-load",
    "main-vang-load",
  ),
  group("Halyard & trim", "main-halyard-load", "main-cunningham-load"),
  group("Locks", "main-halyard-reef-1-lock", "main-boom-reef-1-lock"),
  group("Runners", "main-runner-ps-load", "main-runner-sb-load"),
);

export const MAIN_REEF_2 = dashboard(
  SailId.MainReef2,
  group(
    "Main sail",
    "main-sheet-load",
    "main-traveler-relative-position",
    "main-preventer-load",
    "main-vang-load",
  ),
  group("Halyard & trim", "main-halyard-load"),
  group("Locks", "main-halyard-reef-2-lock", "main-boom-reef-2-lock", "main-cunningham-load"),
  group("Runners", "main-runner-ps-load", "main-runner-sb-load"),
);

export const MAIN_REEF_3 = dashboard(
  SailId.MainReef3,
  group(
    "Main sail",
    "main-sheet-load",
    "main-traveler-relative-position",
    "main-preventer-load",
    "main-vang-load",
  ),
  group("Halyard & trim", "main-halyard-load"),
  group("Locks", "main-halyard-reef-3-lock", "main-boom-reef-3-lock", "main-cunningham-load"),
  group("Runners", "main-runner-ps-load", "main-runner-sb-load"),
);

export const TRISAIL = dashboard(
  SailId.Trisail,
  group("Main sail", "main-sheet-load", "main-traveler-relative-position"),
  group("Runners", "main-runner-ps-load", "main-runner-sb-load"),
  group("Checkstay", "main-checkstay-ps-load", "main-checkstay-sb-load"),
);

export const UTILITY_MAIN = dashboard(
  SailId.UtilityMain,
  group("Main sail", "main-sheet-load", "main-traveler-relative-position", "main-preventer-load"),
  group("Halyard & trim", "main-halyard-load", "main-cunningham-load", "main-outhaul-load"),
  group("Runners", "main-runner-ps-load", "main-runner-sb-load"),
);

export const MIZZEN = dashboard(
  SailId.FullMizzen,
  group("Mizzen sail", "mizzen-sheet-load", "mizzen-preventer-load", "mizzen-vang-load"),
  group("Halyard & trim", "mizzen-halyard-load", "mizzen-cunningham-load", "mizzen-outhaul-load"),
  group("Runners", "mizzen-runner-ps-load", "mizzen-runner-sb-load"),
  group("Checkstay", "mizzen-checkstay-ps-load", "mizzen-checkstay-sb-load"),
);

export const MIZZEN_REEF_1 = dashboard(
  SailId.MizzenReef1,
  group("Mizzen sail", "mizzen-sheet-load", "mizzen-preventer-load", "mizzen-vang-load"),
  group("Halyard and trim", "mizzen-halyard-load"),
  group("Locks", "mizzen-reef-1-lock", "mizzen-boom-reef-1-lock", "mizzen-cunningham-load"),
  group("Runners", "mizzen-runner-ps-load", "mizzen-runner-sb-load"),
);

export const MIZZEN_REEF_2 = dashboard(
  SailId.MizzenReef2,
  group("Mizzen sail", "mizzen-sheet-load", "mizzen-preventer-load", "mizzen-vang-load"),
  group("Halyard and trim", "mizzen-halyard-load"),
  group("Locks", "mizzen-reef-2-lock", "mizzen-boom-reef-2-lock", "mizzen-cunningham-load"),
  group("Runners", "mizzen-runner-ps-load", "mizzen-runner-sb-load"),
);

export const BLADE = dashboard(
  SailId.Blade,
  group("Sheet feeders", "blade-sheet-feeder-ps-load", "blade-sheet-feeder-sb-load"),
  group("Tweakers", "blade-tweaker-ps-load", "blade-tweaker-sb-load"),
  group("Trim", "blade-adjuster-load", "blade-cunningham-load"),
);

export const CODE_ZERO = dashboard(
  SailId.CodeZero,
  group("Tack and halyard", "code-zero-tack-load"),
  group("Locks", "code-zero-lock", "code-zero-overhoist"),
);

export const A3 = dashboard(
  SailId.A3,
  group("Tack and halyard", "code-zero-tack-load"),
  group("Locks", "code-zero-lock", "code-zero-overhoist"),
);

export const A2 = dashboard(
  SailId.A2,
  group("Tack and halyard", "code-zero-tack-load"),
  group("Locks", "code-zero-lock", "code-zero-overhoist"),
);

export const STAYSAIL = dashboard(
  SailId.Staysail,
  group("Sheet feeders", "staysail-sheet-feeder-ps-load", "staysail-sheet-feeder-sb-load"),
  group("Trim", "staysail-stay-adjuster-load"),
);

export const STORM_JIB = dashboard(
  SailId.StormJib,
  group("Locks", "storm-jib-lock", "storm-jib-overhoist"),
);

export const MIZZEN_JIB = dashboard(
  SailId.MizzenJib,
  group("Tack", "mizzen-jib-tack-adjuster-load"),
  group("Locks", "mizzen-jib-lock", "mizzen-jib-overhoist"),
);

export const MIZZEN_STAYSAIL = dashboard(
  SailId.MizzenStaysail,
  group("Tack and halyard", "mizzen-jib-tack-adjuster-load", "mizzen-jib-overhoist"),
  group("Locks", "mizzen-jib-lock"),
);

export const DASHBOARDS: Dashboard[] = [
  OVERVIEW,
  MAIN,
  MAIN_REEF_1,
  MAIN_REEF_2,
  MAIN_REEF_3,
  TRISAIL,
  UTILITY_MAIN,
  MIZZEN,
  MIZZEN_REEF_1,
  MIZZEN_REEF_2,
  BLADE,
  CODE_ZERO,
  A3,
  A2,
  STAYSAIL,
  STORM_JIB,
  MIZZEN_JIB,
  MIZZEN_STAYSAIL,
];
