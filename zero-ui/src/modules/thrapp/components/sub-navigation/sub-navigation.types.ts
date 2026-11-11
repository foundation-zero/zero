import { MimicKey } from "@/modules/thrapp/router/mimics";

export type ModuleGroupKey = "producers" | "buffers" | "consumers";

export type ModuleGroup = {
  key: ModuleGroupKey;
  modules: { key: MimicKey; subModules: MimicKey[] }[];
};

/** A group as the module selector lists it: only modules the current page can show. */
export type ModuleOptionGroup = {
  key: ModuleGroupKey;
  /** `disabled` when the page cannot show the module itself, only some of its sub-modules. */
  modules: { key: MimicKey; disabled: boolean; subModules: MimicKey[] }[];
};

export type ControlState = "automatic" | "manual" | "advisoryDisabled";
