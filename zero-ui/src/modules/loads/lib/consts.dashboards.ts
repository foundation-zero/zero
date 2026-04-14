import { ColumnLayout, FixedColumnsLayout } from "../components/variable-grid/strategies/columns";
import {
  BrokenRowsLayout,
  RowLayout,
  UnbrokenRowsLayout,
} from "../components/variable-grid/strategies/rows";
import { MaybeVariable, PositionId, Variable } from "../types";
import { SailId } from "./consts.sails";
import { VariableId } from "./consts.variables";

export const enum DashboardType {
  Static = "static",
  Dynamic = "dynamic",
}

export const DASHBOARD_TYPES = [DashboardType.Static, DashboardType.Dynamic] as const;

export const isDashboardType = (value: string): value is DashboardType =>
  DASHBOARD_TYPES.includes(value as DashboardType);

export type DashboardId = SailId | DashboardType;

export type Dashboard = {
  id: DashboardId;
  columnLayout: ColumnLayout | RowLayout;
  rowLayout: RowLayout;
  groups: VariableGroup[];
};

export type GroupVariable = [id: VariableId, includeInDynamic?: boolean];

export type VariableGroup<T extends GroupVariable | MaybeVariable | Variable = GroupVariable> = {
  name: string;
  position: PositionId;
  variables: T[];
  includeInDynamic: boolean | SailId[];
};

export const group = (
  name: string,
  position: PositionId,
  ...variables: (VariableId | GroupVariable)[]
): VariableGroup => ({
  name,
  position,
  variables: variables.map((v) => (Array.isArray(v) ? v : [v, true])),
  includeInDynamic: false,
});

export const dynamic = (group: VariableGroup, ...sails: SailId[]): VariableGroup => ({
  ...group,
  includeInDynamic: sails.length > 0 ? sails : true,
});

const dashboard = (
  id: DashboardId,
  columnLayout: ColumnLayout,
  rowLayout: RowLayout,
  ...groups: VariableGroup[]
): Dashboard => ({
  id,
  columnLayout,
  rowLayout,
  groups,
});

export const MAIN_MAST_GROUP = group(
  "Main mast",
  PositionId.Main,
  "main-runner-ps-load",
  "main-runner-sb-load",
  "main-checkstay-ps-load",
  "main-checkstay-sb-load",
  "main-checkstay-deflector-load",
  "main-checkstay-deflector-relative-position",
  "fiber-optic-main-v1-ps",
  "fiber-optic-main-v1-sb",
  "main-headstay-combined-load",
  ["fiber-optic-main-d1-ps", false],
  ["fiber-optic-main-d1-sb", false],
);

export const MAIN_SAIL_GROUP = group(
  "Main sail",
  PositionId.Main,
  "main-sheet-load",
  "main-traveller-relative-position",
  "main-vang-load",
  "main-vang-relative-position",
  "main-cunningham-load",
  "main-preventer-load",
  "main-outhaul-load",
  ["main-outhaul-relative-position", false],
  ["main-halyard-load", false],
);

export const MAIN_LOCKS_GROUP = group(
  "Locks",
  PositionId.Main,
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
  PositionId.Mizzen,
  "mizzen-runner-ps-load",
  "mizzen-runner-sb-load",
  "mizzen-checkstay-ps-load",
  "mizzen-checkstay-sb-load",
  "mizzen-checkstay-deflector-load",
  "mizzen-checkstay-deflector-relative-position",
  "fiber-optic-mizzen-v1-ps",
  "fiber-optic-mizzen-v1-sb",
  "fiber-optic-mizzen-forestay",
  ["fiber-optic-mizzen-d1-ps", false],
  ["fiber-optic-mizzen-d1-sb", false],
);

export const MIZZEN_SAIL_GROUP = group(
  "Mizzen sail",
  PositionId.Mizzen,
  "mizzen-sheet-load",
  "mizzen-vang-load",
  "mizzen-vang-relative-position",
  "mizzen-cunningham-load",
  "mizzen-preventer-load",
  "mizzen-outhaul-load",
  ["mizzen-outhaul-relative-position", false],
  ["mizzen-halyard-load", false],
);

export const MIZZEN_LOCKS_GROUP = group(
  "Locks",
  PositionId.Mizzen,
  "mizzen-halyard-lock-full",
  "mizzen-halyard-lock-1",
  "mizzen-halyard-lock-2",
  "mizzen-halyard-boom-lock-1",
  "mizzen-halyard-boom-lock-2",
);

export const MIZZEN_JIB_GROUP = group(
  "Mizzen jib",
  PositionId.MizzenFore,

  "mizzen-headsail-tack-adjuster-load",
  "mizzen-headsail-tack-adjuster-relative-position",
  "aft-winch-ps-load",
  "aft-winch-sb-load",
);

export const MIZZEN_STAYSAIL_GROUP = group(
  "Mizzen staysail",
  PositionId.MizzenFore,

  "mizzen-headsail-tack-adjuster-load",
  "mizzen-headsail-tack-adjuster-relative-position",
);

export const MIZZEN_HEADSAIL_LOCKS_GROUP = group(
  "Locks",
  PositionId.Mizzen,
  "mizzen-headsail-locks-lock",
);

export const TRISAIL_GROUP = group(
  "Trisail",
  PositionId.Main,
  "main-halyard-load",
  "aft-winch-ps-load",
  "aft-winch-sb-load",
  ["main-traveller-relative-position", false],
  ["main-vang-load", false],
  ["main-vang-relative-position", false],
);

export const TRISAIL_LOCKS_GROUP = group(
  "Locks",
  PositionId.Main,
  "main-halyard-lock-3",
  "main-halyard-boom-lock-3",
);

export const BLADE_GROUP = group(
  "Blade",
  PositionId.ForeOuter,
  "blade-cunningham-load",
  "blade-cunningham-relative-position",
  "blade-sheet-feeder-ps-load",
  "blade-sheet-feeder-sb-load",
  "blade-adjuster-load",
  ["blade-adjuster-relative-position", false],
  ["blade-tweaker-ps-load", false],
  ["blade-tweaker-ps-relative-position", false],
  ["blade-tweaker-sb-load", false],
  ["blade-tweaker-sb-relative-position", false],
);

export const STAYSAIL_GROUP = group(
  "Staysail",
  PositionId.ForeInner,
  "staysail-stay-adjuster-load",
  "staysail-stay-adjuster-relative-position",
  "staysail-sheet-feeder-ps-load",
  "staysail-sheet-feeder-sb-load",
);

export const OUTBOARD_LEAD_GROUP = group(
  "Outboard lead",
  PositionId.ForeInner,
  "primary-winch-ps-load",
  "primary-winch-sb-load",
);

export const STAYSAIL_LOCKS_GROUP = group(
  "Locks",
  PositionId.ForeInner,
  "headsail-locks-lock-staysail",
);

export const A3_GROUP = group(
  "A3",
  PositionId.ForeOuter,
  "code-zero-tack-load",
  "code-zero-tack-relative-position",
  "primary-winch-ps-load",
  "primary-winch-sb-load",
);

export const CODE_ZERO_GROUP = group(
  "Code Zero",
  PositionId.ForeOuter,
  "code-zero-tack-load",
  "code-zero-tack-relative-position",
  "primary-winch-ps-load",
  "primary-winch-sb-load",
);

export const CODE_ZERO_LOCKS_GROUP = group(
  "Locks",
  PositionId.ForeOuter,
  "headsail-locks-lock-a3c0",
);

export const A2_GROUP = group(
  "A2",
  PositionId.ForeOuter,
  "a2-tack-load",
  "primary-winch-ps-load",
  "primary-winch-sb-load",
);

export const A2_LOCKS_GROUP = group("Locks", PositionId.ForeOuter, "headsail-locks-lock-a2");
export const STORM_JIB_GROUP = group(
  "Storm Jib",
  PositionId.ForeInner,
  "storm-jib-tack-load",
  "primary-winch-ps-load",
  "primary-winch-sb-load",
);

export const STORM_JIB_LOCKS_GROUP = group(
  "Locks",
  PositionId.ForeInner,
  "headsail-locks-lock-stormjib",
);

export const OVERVIEW = dashboard(
  DashboardType.Static,
  FixedColumnsLayout,
  BrokenRowsLayout,
  MAIN_MAST_GROUP,
  MIZZEN_MAST_GROUP,
  MAIN_SAIL_GROUP,
  MIZZEN_SAIL_GROUP,
  BLADE_GROUP,
  STAYSAIL_GROUP,
  STORM_JIB_GROUP,
  OUTBOARD_LEAD_GROUP,
  CODE_ZERO_GROUP,
  A3_GROUP,
  A2_GROUP,
  MIZZEN_JIB_GROUP,
  MIZZEN_STAYSAIL_GROUP,
);

export const MAIN = dashboard(
  SailId.FullMain,
  UnbrokenRowsLayout,
  UnbrokenRowsLayout,
  MAIN_MAST_GROUP,
  MAIN_SAIL_GROUP,
  MAIN_LOCKS_GROUP,
);
export const MAIN_REEF_1 = dashboard(
  SailId.MainReef1,
  UnbrokenRowsLayout,
  UnbrokenRowsLayout,
  MAIN_MAST_GROUP,
  MAIN_SAIL_GROUP,
  MAIN_LOCKS_GROUP,
);
export const MAIN_REEF_2 = dashboard(
  SailId.MainReef2,
  UnbrokenRowsLayout,
  UnbrokenRowsLayout,
  MAIN_MAST_GROUP,
  MAIN_SAIL_GROUP,
  MAIN_LOCKS_GROUP,
);
export const MAIN_REEF_3 = dashboard(
  SailId.MainReef3,
  UnbrokenRowsLayout,
  UnbrokenRowsLayout,
  MAIN_MAST_GROUP,
  MAIN_SAIL_GROUP,
  MAIN_LOCKS_GROUP,
);

export const UTILITY_MAIN = dashboard(
  SailId.UtilityMain,
  UnbrokenRowsLayout,
  UnbrokenRowsLayout,
  MAIN_MAST_GROUP,
  MAIN_SAIL_GROUP,
  MAIN_LOCKS_GROUP,
);

export const TRISAIL = dashboard(
  SailId.Trisail,
  UnbrokenRowsLayout,
  UnbrokenRowsLayout,
  TRISAIL_GROUP,
  TRISAIL_LOCKS_GROUP,
);

export const MIZZEN = dashboard(
  SailId.FullMizzen,
  UnbrokenRowsLayout,
  UnbrokenRowsLayout,
  MIZZEN_MAST_GROUP,
  MIZZEN_SAIL_GROUP,
  MIZZEN_LOCKS_GROUP,
);

export const MIZZEN_REEF_1 = dashboard(
  SailId.MizzenReef1,
  UnbrokenRowsLayout,
  UnbrokenRowsLayout,
  MIZZEN_MAST_GROUP,
  MIZZEN_SAIL_GROUP,
  MIZZEN_LOCKS_GROUP,
);

export const MIZZEN_REEF_2 = dashboard(
  SailId.MizzenReef2,
  UnbrokenRowsLayout,
  UnbrokenRowsLayout,
  MIZZEN_MAST_GROUP,
  MIZZEN_SAIL_GROUP,
  MIZZEN_LOCKS_GROUP,
);

export const MIZZEN_JIB = dashboard(
  SailId.MizzenJib,
  UnbrokenRowsLayout,
  UnbrokenRowsLayout,
  MIZZEN_MAST_GROUP,
  MIZZEN_JIB_GROUP,
  group("Main", PositionId.Main, "main-traveller-relative-position", "main-preventer-load"),
  MIZZEN_HEADSAIL_LOCKS_GROUP,
);

export const MIZZEN_STAYSAIL = dashboard(
  SailId.MizzenStaysail,
  UnbrokenRowsLayout,
  UnbrokenRowsLayout,
  MIZZEN_MAST_GROUP,
  MIZZEN_STAYSAIL_GROUP,
  MIZZEN_HEADSAIL_LOCKS_GROUP,
);

export const STORM_JIB = dashboard(
  SailId.StormJib,
  UnbrokenRowsLayout,
  UnbrokenRowsLayout,
  STORM_JIB_GROUP,
  OUTBOARD_LEAD_GROUP,
  STORM_JIB_LOCKS_GROUP,
);

export const STAYSAIL = dashboard(
  SailId.Staysail,
  UnbrokenRowsLayout,
  UnbrokenRowsLayout,
  MAIN_MAST_GROUP,
  STAYSAIL_GROUP,
  OUTBOARD_LEAD_GROUP,
  STAYSAIL_LOCKS_GROUP,
);

export const BLADE = dashboard(
  SailId.Blade,
  UnbrokenRowsLayout,
  UnbrokenRowsLayout,
  MAIN_MAST_GROUP,
  BLADE_GROUP,
  OUTBOARD_LEAD_GROUP,
);

export const CODE_ZERO = dashboard(
  SailId.CodeZero,
  UnbrokenRowsLayout,
  UnbrokenRowsLayout,
  MAIN_MAST_GROUP,
  CODE_ZERO_GROUP,
  CODE_ZERO_LOCKS_GROUP,
);

export const DYNAMIC = dashboard(
  DashboardType.Dynamic,
  FixedColumnsLayout,
  UnbrokenRowsLayout,
  dynamic(MAIN_MAST_GROUP),
  dynamic(MIZZEN_MAST_GROUP),
  dynamic(
    MAIN_SAIL_GROUP,
    SailId.FullMain,
    SailId.MainReef1,
    SailId.MainReef2,
    SailId.MainReef3,
    SailId.Trisail,
    SailId.UtilityMain,
  ),
  dynamic(MIZZEN_SAIL_GROUP, SailId.FullMizzen, SailId.MizzenReef1, SailId.MizzenReef2),
  dynamic(A2_GROUP, SailId.A2),
  dynamic(BLADE_GROUP, SailId.Blade),
  dynamic(STAYSAIL_GROUP, SailId.Staysail),
  dynamic(CODE_ZERO_GROUP, SailId.CodeZero),
  dynamic(STORM_JIB_GROUP, SailId.StormJib),
  dynamic(MIZZEN_JIB_GROUP, SailId.MizzenJib),
  dynamic(MIZZEN_STAYSAIL_GROUP, SailId.MizzenStaysail),
  dynamic(OUTBOARD_LEAD_GROUP, SailId.Staysail, SailId.StormJib),
  dynamic(TRISAIL_GROUP, SailId.Trisail),
);

export const A3 = dashboard(
  SailId.A3,
  UnbrokenRowsLayout,
  UnbrokenRowsLayout,
  MAIN_MAST_GROUP,
  CODE_ZERO_GROUP,
  CODE_ZERO_LOCKS_GROUP,
);

export const A2 = dashboard(
  SailId.A2,
  UnbrokenRowsLayout,
  UnbrokenRowsLayout,
  MAIN_MAST_GROUP,
  A2_GROUP,
  A2_LOCKS_GROUP,
);

export const DASHBOARDS: Dashboard[] = [
  OVERVIEW,
  DYNAMIC,
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
