import { PvtMode } from "@/modules/thrsim/types";
import { MimicComponentState } from "../index.ts";

export { default as PvtTitle } from "../circuit-box/CircuitBoxTitle.vue";
export { default as Pvt } from "./Pvt.vue";
export { default as PvtMode } from "./PvtMode.vue";

export const PVT_MODE_COLORS: Record<PvtMode | MimicComponentState, string> = {
  [PvtMode.Recovery]: "var(--constructive)",
  [PvtMode.Idle]: "var(--muted-foreground)",
  [MimicComponentState.Manual]: "var(--warning)",
  [MimicComponentState.Alarm]: "var(--destructive)",
  [MimicComponentState.Normal]: "var(--constructive)",
};
