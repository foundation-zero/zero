export { default as BoilerTankTitle } from "../circuit-box/CircuitBoxTitle.vue";
export { default as BoilerTank } from "./BoilerTank.vue";
export { default as BoilerTankLevel } from "./BoilerTankLevel.vue";
export { default as BoilerTankLevelIndicator } from "./BoilerTankLevelIndicator.vue";
export { default as BoilerTankMode } from "./BoilerTankMode.vue";

export const BOILER_TANK_WIDTH = 204;
export const BOILER_TANK_HEIGHT = 148;
export const BOILER_TANK_LEVEL_WAVE_HEIGHT = 21;
export const BOILER_TANK_LEVEL_LINE_OFFSET = 13;

export const enum BoilerTankModes {
  InUse = "in-use",
  Boosting = "boosting",
  Standby = "standby",
}

export const BOILER_TANK_MODE_COLORS: Record<BoilerTankModes, string> = {
  [BoilerTankModes.InUse]: "var(--constructive)",
  [BoilerTankModes.Boosting]: "var(--heating-medium)",
  [BoilerTankModes.Standby]: "var(--muted-foreground)",
};
