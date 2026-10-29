import { toFieldsMap } from "../../modules";
import { ADSORPTION_ASSET_DATA } from "./assets";
import { ADSORPTION_EXCHANGE_CIRCUIT_DATA } from "./exchange-circuits";
import { ADSORPTION_EXPANSION_TANK_DATA } from "./expansion-tanks";
import { ADSORPTION_EXPANSION_VALVE_DATA } from "./expansion-valves";
import { ADSORPTION_FLOW_CONTROL_VALVE_DATA } from "./flow-control-valves";
import { ADSORPTION_FLOW_SENSOR_DATA } from "./flow-sensors";
import { ADSORPTION_HEAT_EXCHANGER_DATA } from "./heat-exchangers";
import { ADSORPTION_MANUAL_VALVE_DATA } from "./manual-valves";
import { ADSORPTION_MIX_VALVE_DATA } from "./mix-valves";
import { ADSORPTION_PRESSURE_GAUGE_DATA } from "./pressure-gauges";
import { ADSORPTION_SWITCH_VALVE_DATA } from "./switch-valves";
import { ADSORPTION_TEMPERATURE_SENSOR_DATA } from "./temperature-sensors";

export { ADSORPTION_ASSET_DATA } from "./assets";
export { ADSORPTION_EXCHANGE_CIRCUIT_DATA } from "./exchange-circuits";
export { ADSORPTION_EXPANSION_TANK_DATA } from "./expansion-tanks";
export { ADSORPTION_EXPANSION_VALVE_DATA } from "./expansion-valves";
export { ADSORPTION_FLOW_CONTROL_VALVE_DATA } from "./flow-control-valves";
export { ADSORPTION_FLOW_SENSOR_DATA } from "./flow-sensors";
export { ADSORPTION_HEAT_EXCHANGER_DATA } from "./heat-exchangers";
export { ADSORPTION_MANUAL_VALVE_DATA } from "./manual-valves";
export { ADSORPTION_MIX_VALVE_DATA } from "./mix-valves";
export { ADSORPTION_PRESSURE_GAUGE_DATA } from "./pressure-gauges";
export { ADSORPTION_SWITCH_VALVE_DATA } from "./switch-valves";
export { ADSORPTION_TEMPERATURE_SENSOR_DATA } from "./temperature-sensors";

export const ADSORPTION_MIMIC_DATA = toFieldsMap({
  ...ADSORPTION_ASSET_DATA,
  ...ADSORPTION_EXCHANGE_CIRCUIT_DATA,
  ...ADSORPTION_EXPANSION_TANK_DATA,
  ...ADSORPTION_EXPANSION_VALVE_DATA,
  ...ADSORPTION_FLOW_CONTROL_VALVE_DATA,
  ...ADSORPTION_FLOW_SENSOR_DATA,
  ...ADSORPTION_HEAT_EXCHANGER_DATA,
  ...ADSORPTION_MANUAL_VALVE_DATA,
  ...ADSORPTION_MIX_VALVE_DATA,
  ...ADSORPTION_PRESSURE_GAUGE_DATA,
  ...ADSORPTION_SWITCH_VALVE_DATA,
  ...ADSORPTION_TEMPERATURE_SENSOR_DATA,
});
