export { default as HeatPumpTitle } from "../circuit-box/CircuitBoxTitle.vue";
export { default as HeatPump } from "./HeatPump.vue";
export { default as HeatPumpMode } from "./HeatPumpMode.vue";

export const enum HeatPumpModes {
  Active = "active",
  Inactive = "inactive",
}

export const HEAT_PUMP_MODE_COLORS: Record<HeatPumpModes, string> = {
  [HeatPumpModes.Active]: "var(--constructive)",
  [HeatPumpModes.Inactive]: "var(--muted-foreground)",
};
