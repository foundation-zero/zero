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

export const MAIN_MAST_GROUP = group(
  "Main mast",
  "main-runner-ps-load",
  "main-runner-sb-load",
  "main-checkstay-ps-load",
  "main-checkstay-sb-load",
  "main-checkstay-deflector-load",
  "main-checkstay-deflector-relative-position",
  "combined-headstay-load",
);

export const MAIN_SAIL_GROUP = group(
  "Main sail",
  "main-sheet-load",
  "main-traveller-relative-position",
  "main-vang-relative-position",
  // "main-vang-load",
  "main-cunningham-load",
  "main-outhaul-load",
  "main-outhaul-relative-position",
  "main-preventer-load",
);

export const MAIN_LOCKS_GROUP = group(
  "Locks",
  "main-halyard-lock-full",
  "main-halyard-lock-1",
  "main-halyard-lock-2",
  "main-halyard-lock-3",
  "main-halyard-boom-lock-1",
  "main-halyard-boom-lock-2",
  "main-halyard-boom-lock-3",
);

export const MIZZEN_MAST_GROUP = group(
  "Mizzen mast",
  "mizzen-runner-ps-load",
  "mizzen-runner-sb-load",
  "mizzen-checkstay-ps-load",
  "mizzen-checkstay-sb-load",
  "mizzen-checkstay-deflector-load",
  "mizzen-checkstay-deflector-relative-position",
);

export const MIZZEN_SAIL_GROUP = group(
  "Mizzen sail",
  "mizzen-sheet-load",
  "mizzen-vang-relative-position",
  // "mizzen-vang-load",
  "mizzen-cunningham-load",
  "mizzen-outhaul-load",
  "mizzen-outhaul-relative-position",
  "mizzen-preventer-load",
);

export const MIZZEN_LOCKS_GROUP = group(
  "Locks",
  "mizzen-halyard-lock-full",
  "mizzen-halyard-lock-1",
  "mizzen-halyard-lock-2",
  "mizzen-halyard-boom-lock-1",
  "mizzen-halyard-boom-lock-2",
);

export const MIZZEN_JIB_GROUP = group(
  "Mizzen jib",
  "mizzen-headsail-tack-adjuster-load",
  "mizzen-headsail-tack-adjuster-relative-position",
  "aft-winch-ps-load",
  "aft-winch-sb-load",
);

export const MIZZEN_STAYSAIL_GROUP = group(
  "Mizzen staysail",
  "mizzen-headsail-tack-adjuster-load",
  "mizzen-headsail-tack-adjuster-relative-position",
);

export const MIZZEN_HEADSAIL_LOCKS_GROUP = group("Locks", "mizzen-headsail-locks-lock");

export const TRISAIL_GROUP = group(
  "Trisail",
  "main-sheet-load",
  "main-traveller-relative-position",
  "main-vang-relative-position",
  // "main-vang-load",
  "main-outhaul-load",
  "main-outhaul-relative-position",
  "main-preventer-load",
  "main-halyard-load",
  "aft-winch-ps-load",
  "aft-winch-sb-load",
);

export const TRISAIL_LOCKS_GROUP = group(
  "Locks",
  "main-halyard-lock-full",
  "main-halyard-lock-3",
  "main-halyard-boom-lock-3",
);

export const BLADE_SAIL_GROUP = group(
  "Blade",
  "blade-adjuster-load",
  "blade-adjuster-relative-position",
  "blade-cunningham-load",
  "blade-cunningham-relative-position",
  "blade-sheet-feeder-ps-load",
  "blade-tweaker-ps-load",
  "blade-tweaker-ps-relative-position",
  "blade-sheet-feeder-sb-load",
  "blade-tweaker-sb-load",
  "blade-tweaker-sb-relative-position",
);

export const STAYSAIL_GROUP = group(
  "Staysail",
  "staysail-stay-adjuster-load",
  "staysail-stay-adjuster-relative-position",
  "staysail-sheet-feeder-ps-load",
  "staysail-sheet-feeder-sb-load",
);

export const OUTBOARD_LEAD_GROUP = group(
  "Outboard lead",
  "primary-winch-ps-load",
  "primary-winch-sb-load",
);

export const STAYSAIL_LOCKS_GROUP = group("Locks", "headsail-locks-lock-staysail");

export const CODE_ZERO_GROUP = group(
  "Code Zero",
  "code-zero-tack-load",
  "code-zero-tack-relative-position",
  "primary-winch-ps-load",
  "primary-winch-sb-load",
);

export const CODE_ZERO_LOCKS_GROUP = group("Locks", "headsail-locks-lock-a3c0");

export const A2_GROUP = group(
  "A2",
  "a2-tack-load",
  "primary-winch-ps-load",
  "primary-winch-sb-load",
);

export const A2_LOCKS_GROUP = group("Locks", "headsail-locks-lock-a2");
export const STORM_JIB_GROUP = group(
  "Storm Jib",
  "storm-jib-tack-load",
  "primary-winch-ps-load",
  "primary-winch-sb-load",
);

export const STORM_JIB_LOCKS_GROUP = group("Locks", "headsail-locks-lock-stormjib");

export const OVERVIEW = dashboard(
  SailId.None,
  MAIN_MAST_GROUP,
  MAIN_SAIL_GROUP,
  MIZZEN_MAST_GROUP,
  MIZZEN_SAIL_GROUP,
  BLADE_SAIL_GROUP,
  STAYSAIL_GROUP,
  CODE_ZERO_GROUP,
  STORM_JIB_GROUP,
);

export const MAIN = dashboard(SailId.FullMain, MAIN_MAST_GROUP, MAIN_SAIL_GROUP, MAIN_LOCKS_GROUP);
export const MAIN_REEF_1 = dashboard(
  SailId.MainReef1,
  MAIN_MAST_GROUP,
  MAIN_SAIL_GROUP,
  MAIN_LOCKS_GROUP,
);
export const MAIN_REEF_2 = dashboard(
  SailId.MainReef2,
  MAIN_MAST_GROUP,
  MAIN_SAIL_GROUP,
  MAIN_LOCKS_GROUP,
);
export const MAIN_REEF_3 = dashboard(
  SailId.MainReef3,
  MAIN_MAST_GROUP,
  MAIN_SAIL_GROUP,
  MAIN_LOCKS_GROUP,
);

export const UTILITY_MAIN = dashboard(
  SailId.UtilityMain,
  MAIN_MAST_GROUP,
  MAIN_SAIL_GROUP,
  MAIN_LOCKS_GROUP,
);

export const TRISAIL = dashboard(SailId.Trisail, TRISAIL_GROUP, TRISAIL_LOCKS_GROUP);

export const MIZZEN = dashboard(
  SailId.FullMizzen,
  MIZZEN_MAST_GROUP,
  MIZZEN_SAIL_GROUP,
  MIZZEN_LOCKS_GROUP,
);

export const MIZZEN_REEF_1 = dashboard(
  SailId.MizzenReef1,
  MIZZEN_MAST_GROUP,
  MIZZEN_SAIL_GROUP,
  MIZZEN_LOCKS_GROUP,
);

export const MIZZEN_REEF_2 = dashboard(
  SailId.MizzenReef2,
  MIZZEN_MAST_GROUP,
  MIZZEN_SAIL_GROUP,
  MIZZEN_LOCKS_GROUP,
);

export const MIZZEN_JIB = dashboard(
  SailId.MizzenJib,
  MIZZEN_MAST_GROUP,
  MIZZEN_JIB_GROUP,
  group("Main", "main-traveller-relative-position", "main-preventer-load"),
  MIZZEN_HEADSAIL_LOCKS_GROUP,
);

export const MIZZEN_STAYSAIL = dashboard(
  SailId.MizzenStaysail,
  MIZZEN_MAST_GROUP,
  MIZZEN_STAYSAIL_GROUP,
  MIZZEN_HEADSAIL_LOCKS_GROUP,
);

export const STORM_JIB = dashboard(
  SailId.StormJib,
  STORM_JIB_GROUP,
  OUTBOARD_LEAD_GROUP,
  STORM_JIB_LOCKS_GROUP,
);

export const STAYSAIL = dashboard(
  SailId.Staysail,
  MAIN_MAST_GROUP,
  STAYSAIL_GROUP,
  OUTBOARD_LEAD_GROUP,
  STAYSAIL_LOCKS_GROUP,
);

export const BLADE = dashboard(
  SailId.Blade,
  MAIN_MAST_GROUP,
  BLADE_SAIL_GROUP,
  OUTBOARD_LEAD_GROUP,
);

export const CODE_ZERO = dashboard(
  SailId.CodeZero,
  MAIN_MAST_GROUP,
  CODE_ZERO_GROUP,
  CODE_ZERO_LOCKS_GROUP,
);

export const A3 = dashboard(SailId.A3, MAIN_MAST_GROUP, CODE_ZERO_GROUP, CODE_ZERO_LOCKS_GROUP);

export const A2 = dashboard(SailId.A2, MAIN_MAST_GROUP, A2_GROUP, A2_LOCKS_GROUP);

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
