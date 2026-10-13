import { toFieldsMap } from "../..";
import { DHW_ASSET_DATA } from "./assets";
import { DHW_TANK_DATA } from "./boiler-tanks";
import { DHW_CONNECTING_CIRCUIT_DATA } from "./connecting-circuits";
import { DHW_EXCHANGE_CIRCUIT_DATA } from "./exchange-circuits";
import { DHW_FLOW_CONTROL_VALVE_DATA } from "./flow-control-valves";
import { DHW_FLOW_SENSOR_DATA } from "./flow-sensors";
import { DHW_HEAT_EXCHANGER_DATA } from "./heat-exchangers";
import { DHW_LEVEL_SENSOR_DATA } from "./level-sensors";
import { DHW_LEVEL_SWITCH_DATA } from "./level-switches";
import { DHW_MANUAL_VALVE_DATA } from "./manual-valves";
import { DHW_PRESSURE_SENSOR_DATA } from "./pressure-sensors";
import { DHW_PUMP_DATA } from "./pumps";
import { DHW_SWITCH_VALVE_DATA } from "./switch-valves";
import { DHW_TEMPERATURE_SENSOR_DATA } from "./temperature-sensors";

export { DHW_ASSET_DATA } from "./assets";
export { DHW_TANK_DATA } from "./boiler-tanks";
export { DHW_CONNECTING_CIRCUIT_DATA } from "./connecting-circuits";
export { DHW_EXCHANGE_CIRCUIT_DATA } from "./exchange-circuits";
export { DHW_FLOW_CONTROL_VALVE_DATA } from "./flow-control-valves";
export { DHW_FLOW_SENSOR_DATA } from "./flow-sensors";
export { DHW_HEAT_EXCHANGER_DATA } from "./heat-exchangers";
export { DHW_LEVEL_SENSOR_DATA } from "./level-sensors";
export { DHW_LEVEL_SWITCH_DATA } from "./level-switches";
export { DHW_MANUAL_VALVE_DATA } from "./manual-valves";
export { DHW_PRESSURE_SENSOR_DATA } from "./pressure-sensors";
export { DHW_PUMP_DATA } from "./pumps";
export { DHW_SWITCH_VALVE_DATA } from "./switch-valves";
export { DHW_TEMPERATURE_SENSOR_DATA } from "./temperature-sensors";

export const DHW_MIMIC_DATA = toFieldsMap({
  ...DHW_TANK_DATA,
  ...DHW_SWITCH_VALVE_DATA,
  ...DHW_FLOW_CONTROL_VALVE_DATA,
  ...DHW_HEAT_EXCHANGER_DATA,
  ...DHW_PUMP_DATA,
  ...DHW_MANUAL_VALVE_DATA,
  ...DHW_PRESSURE_SENSOR_DATA,
  ...DHW_FLOW_SENSOR_DATA,
  ...DHW_TEMPERATURE_SENSOR_DATA,
  ...DHW_LEVEL_SENSOR_DATA,
  ...DHW_LEVEL_SWITCH_DATA,
  ...DHW_ASSET_DATA,
  ...DHW_CONNECTING_CIRCUIT_DATA,
  ...DHW_EXCHANGE_CIRCUIT_DATA,
});
