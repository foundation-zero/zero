import { toFieldsMap } from "../..";
import { BOILER_TANK_DATA } from "./boiler-tanks";
import { BOILER_SWITCH_VALVE_DATA } from "./switch-valves";

export * from "./boiler-tanks";
export * from "./switch-valves";

export const BOILERS_MIMIC_DATA = toFieldsMap({
  ...BOILER_TANK_DATA,
  ...BOILER_SWITCH_VALVE_DATA,
});
