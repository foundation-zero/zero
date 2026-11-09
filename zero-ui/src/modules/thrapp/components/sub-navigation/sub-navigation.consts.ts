import { ModuleGroup } from "./sub-navigation.types";

/** Modules in the module selector, grouped by their role and sorted by name. */
export const MODULE_GROUPS: ModuleGroup[] = [
  {
    key: "producers",
    modules: [
      { key: "dc", subModules: [] },
      { key: "drives", subModules: [] },
      { key: "pvt", subModules: ["pvt-main", "pvt-owners", "pvt-main-heat"] },
      { key: "thrusters", subModules: [] },
    ],
  },
  {
    key: "buffers",
    modules: [
      { key: "dhw", subModules: [] },
      { key: "pcm", subModules: [] },
    ],
  },
  {
    key: "consumers",
    modules: [{ key: "adsorption", subModules: [] }],
  },
];
