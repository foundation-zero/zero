export type Dashboard = {
  name: string;
  sail?: string;
  groups: VariableGroup[];
};

export type VariableGroup = {
  name: string;
  variables: string[];
};

export const group = (name: string, ...variables: string[]): VariableGroup => ({
  name,
  variables,
});

const dashboard = (
  name: string,
  sail: string | undefined,
  ...groups: VariableGroup[]
): Dashboard => ({
  name,
  sail,
  groups,
});

export const OVERVIEW = dashboard(
  "loads.dashboards.overview",
  undefined,
  group("Mizzen", "mizzen-sheet-load", "mizzen-preventer-load", "mizzen-vang-load"),
  group("Mizzen foresails", "mizzen-sheet-load"),
  group(
    "Main",
    "main-sheet-load",
    "main-traveler-position",
    "main-preventer-load",
    "main-vang-load",
  ),
  group("Main foresails", "main-sheet-load"),
  group(
    "Mizzen Rig",
    "mizzen-runner-load-ps",
    "mizzen-runner-load-sb",
    "mizzen-checkstay-load-ps",
    "mizzen-checkstay-load-sb",
  ),
  group("Mast locks", "main-reef-1-lock", "main-reef-2-lock", "main-reef-3-lock"),
);
