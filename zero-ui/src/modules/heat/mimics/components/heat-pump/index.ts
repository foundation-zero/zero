import { ModeBadgeMode } from "../mode-badge";

export { default as HeatPumpMode } from "./HeatPumpMode.vue";

export const enum HeatPumpModes {
  Active = "active",
  Inactive = "inactive",
}

export const HEAT_PUMP_MODE_COLORS: Record<HeatPumpModes, ModeBadgeMode> = {
  [HeatPumpModes.Active]: ModeBadgeMode.Active,
  [HeatPumpModes.Inactive]: ModeBadgeMode.Idle,
};
