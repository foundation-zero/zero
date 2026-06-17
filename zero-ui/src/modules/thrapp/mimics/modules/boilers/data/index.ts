import { toFieldsMap } from "../..";
import { BOILER_ASSET_DATA } from "./assets";
import { BOILER_TANK_DATA } from "./boiler-tanks";
import { BOILER_EXCHANGE_CIRCUIT_DATA } from "./exchange-circuits";
import { BOILER_FLOW_CONTROL_VALVE_DATA } from "./flow-control-valves";
import { BOILER_FLOW_SENSOR_DATA } from "./flow-sensors";
import { BOILER_HEAT_EXCHANGER_DATA } from "./heat-exchangers";
import { BOILER_HOT_WATER_CIRCUIT_DATA } from "./hot-water-circuits";
import { BOILER_MANUAL_VALVE_DATA } from "./manual-valves";
import { BOILER_PRESSURE_SENSOR_DATA } from "./pressure-sensors";
import { BOILER_PUMP_DATA } from "./pumps";
import { BOILER_SWITCH_VALVE_DATA } from "./switch-valves";
import { BOILER_TEMPERATURE_SENSOR_DATA } from "./temperature-sensors";

export { BOILER_ASSET_DATA } from "./assets";
export { BOILER_TANK_DATA } from "./boiler-tanks";
export { BOILER_EXCHANGE_CIRCUIT_DATA } from "./exchange-circuits";
export { BOILER_FLOW_CONTROL_VALVE_DATA } from "./flow-control-valves";
export { BOILER_FLOW_SENSOR_DATA } from "./flow-sensors";
export { BOILER_HEAT_EXCHANGER_DATA } from "./heat-exchangers";
export { BOILER_HOT_WATER_CIRCUIT_DATA } from "./hot-water-circuits";
export { BOILER_MANUAL_VALVE_DATA } from "./manual-valves";
export { BOILER_PRESSURE_SENSOR_DATA } from "./pressure-sensors";
export { BOILER_PUMP_DATA } from "./pumps";
export { BOILER_SWITCH_VALVE_DATA } from "./switch-valves";
export { BOILER_TEMPERATURE_SENSOR_DATA } from "./temperature-sensors";

export const BOILERS_MIMIC_DATA = toFieldsMap({
  ...BOILER_TANK_DATA,
  ...BOILER_SWITCH_VALVE_DATA,
  ...BOILER_FLOW_CONTROL_VALVE_DATA,
  ...BOILER_HEAT_EXCHANGER_DATA,
  ...BOILER_PUMP_DATA,
  ...BOILER_MANUAL_VALVE_DATA,
  ...BOILER_PRESSURE_SENSOR_DATA,
  ...BOILER_FLOW_SENSOR_DATA,
  ...BOILER_TEMPERATURE_SENSOR_DATA,
  ...BOILER_ASSET_DATA,
  ...BOILER_HOT_WATER_CIRCUIT_DATA,
  ...BOILER_EXCHANGE_CIRCUIT_DATA,
});
