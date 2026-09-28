import { MimicComponentState } from "../index.ts";
import { ModeBadgeMode } from "../mode-badge";

export { default as HeatPumpTitle } from "../circuit-box/CircuitBoxTitle.vue";
export { default as HeatPump } from "./HeatPump.vue";
export { default as HeatPumpMode } from "./HeatPumpMode.vue";

export const enum HeatPumpModes {
  Active = "active",
  Inactive = "inactive",
}

export const HEAT_PUMP_MODE_COLORS: Record<HeatPumpModes | MimicComponentState, ModeBadgeMode> = {
  [HeatPumpModes.Active]: ModeBadgeMode.Active,
  [HeatPumpModes.Inactive]: ModeBadgeMode.Idle,
  [MimicComponentState.Manual]: ModeBadgeMode.ManualControl,
  [MimicComponentState.Alarm]: ModeBadgeMode.AdvisoryOff,
  [MimicComponentState.Normal]: ModeBadgeMode.Active,
};
