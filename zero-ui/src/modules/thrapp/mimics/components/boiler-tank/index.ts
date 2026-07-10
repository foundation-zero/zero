import { BoilerTankState } from "@/modules/thrs/types/index.ts";
import { MimicComponentState } from "../index.ts";

export { default as BoilerTankTitle } from "../circuit-box/CircuitBoxTitle.vue";
export { default as BoilerTank } from "./BoilerTank.vue";
export { default as BoilerTankLevel } from "./BoilerTankLevel.vue";
export { default as BoilerTankLevelIndicator } from "./BoilerTankLevelIndicator.vue";
export { default as BoilerTankMode } from "./BoilerTankMode.vue";

export const DHW_TANK_WIDTH = 204;
export const DHW_TANK_HEIGHT = 148;
export const DHW_TANK_LEVEL_WAVE_HEIGHT = 21;
export const DHW_TANK_LEVEL_LINE_OFFSET = 13;

export const DHW_TANK_MODE_COLORS: Record<BoilerTankState | MimicComponentState, string> = {
  [BoilerTankState.InUse]: "var(--constructive)",
  [BoilerTankState.Boosting]: "var(--heating-medium)",
  [BoilerTankState.Standby]: "var(--muted-foreground)",
  [MimicComponentState.Manual]: "var(--warning)",
  [MimicComponentState.Alarm]: "var(--destructive)",
  [MimicComponentState.Normal]: "var(--constructive)",
  [BoilerTankState.Disabled]: "var(--destructive-muted)",

  // Verify these colors with Figma
  [BoilerTankState.Filling]: "var(--constructive)",
  [BoilerTankState.NeedsBoost]: "var(--muted-foreground)",
  [BoilerTankState.NeedsFill]: "var(--muted-foreground)",
};
