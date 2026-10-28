import { PvtMode } from "@/modules/thrapp/types/thrs";
import { ModeBadgeMode } from "../mode-badge";

export { default as PvtMode } from "./PvtMode.vue";

export const PVT_MODE_COLORS: Record<PvtMode, ModeBadgeMode> = {
  [PvtMode.Recovery]: ModeBadgeMode.Active,
  [PvtMode.Warmup]: ModeBadgeMode.BoostingLow,
  [PvtMode.Idle]: ModeBadgeMode.Idle,
};
