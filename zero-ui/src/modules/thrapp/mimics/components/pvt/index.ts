import { PvtMode } from "@/modules/thrsim/types";
import { ModeBadgeMode } from "../mode-badge";

export { default as PvtMode } from "./PvtMode.vue";

export const PVT_MODE_COLORS: Record<PvtMode, ModeBadgeMode> = {
  [PvtMode.Recovery]: ModeBadgeMode.Active,
  [PvtMode.Idle]: ModeBadgeMode.Idle,
};
