import { DcMode } from "@/modules/thrapp/types/thrs";
import { ModeBadgeMode } from "../mode-badge";

export const DC_CONVERTER_WIDTH = 200;
export const DC_CONVERTER_HEIGHT = 205;

export const DC_MODE_COLORS: Record<DcMode, ModeBadgeMode> = {
  [DcMode.Recovery]: ModeBadgeMode.Active,
  [DcMode.Idle]: ModeBadgeMode.Idle,
};
