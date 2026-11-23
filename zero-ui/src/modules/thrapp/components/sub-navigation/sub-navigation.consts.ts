import { MimicKey } from "@/modules/thrapp/router/mimics";
import { ModuleGroup } from "./sub-navigation.types";

/** Modules in the module selector, grouped by their role and sorted by name. */
export const MODULE_GROUPS: ModuleGroup[] = [
  {
    key: "producers",
    modules: [
      { key: "dc", subModules: ["dc-aft", "dc-ugrid", "dc-fwd"] },
      { key: "drives", subModules: ["drives-shorepower"] },
      { key: "pvt", subModules: ["pvt-main", "pvt-owners"] },
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

/**
 * The mode targets a sub-module shows, when it covers only some of its module's targets. The PVT
 * biminis show the state of their own groups: main bimini 9001-01 (FWD) and 9002-01 (AFT), owners
 * bimini 9001-03.
 */
export const SUB_MODULE_MODE_TARGETS: Partial<Record<MimicKey, string[]>> = {
  "pvt-main": ["fwd", "aft"],
  "pvt-owners": ["owners"],
};
