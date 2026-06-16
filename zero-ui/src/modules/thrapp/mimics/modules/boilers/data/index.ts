import { toFieldsMap } from "../..";
import { BOILER_TANK_DATA } from "./boiler-tanks";
import { BOILER_FLOW_CONTROL_VALVE_DATA } from "./flow-control-valves";
import { BOILER_HEAT_EXCHANGER_DATA } from "./heat-exchangers";
import { BOILER_PUMP_DATA } from "./pumps";
import { BOILER_SWITCH_VALVE_DATA } from "./switch-valves";

export * from "./boiler-tanks";
export * from "./flow-control-valves";
export * from "./heat-exchangers";
export * from "./pumps";
export * from "./switch-valves";

export const BOILERS_MIMIC_DATA = toFieldsMap({
  ...BOILER_TANK_DATA,
  ...BOILER_SWITCH_VALVE_DATA,
  ...BOILER_FLOW_CONTROL_VALVE_DATA,
  ...BOILER_HEAT_EXCHANGER_DATA,
  ...BOILER_PUMP_DATA,
});
