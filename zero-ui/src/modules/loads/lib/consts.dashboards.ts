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
  group("Mizzen", "mizzen-preventer-load", "mizzen-vang-load"),
  group("Mizzen foresails"),
  group("Main", "main-traveler-relative-position", "main-preventer-load", "main-vang-load"),
  group(
    "Main foresails",
    "blade-sheet-feeder-ps-load",
    "blade-sheet-feeder-sb-load",
    "staysail-sheet-feeder-ps-load",
    "staysail-sheet-feeder-sb-load",
  ),
  group(
    "Mizzen Rig",
    "mizzen-runner-ps-load",
    "mizzen-runner-sb-load",
    "mizzen-checkstay-ps-load",
    "mizzen-checkstay-sb-load",
  ),
  group(
    "Mast locks",
    "main-halyard-reef-1-lock",
    "main-halyard-reef-2-lock",
    "main-halyard-reef-3-lock",
  ),
);

export const MIZZEN_JIb = dashboard(
  SailId.MizzenJib,
  group("Sail", "mizzen-runner-ps-load", "mizzen-runner-sb-load"),
);

export const DASHBOARDS: Dashboard[] = [OVERVIEW, MIZZEN_JIb];
