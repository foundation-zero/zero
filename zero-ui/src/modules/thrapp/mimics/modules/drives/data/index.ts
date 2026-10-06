import { toFieldsMap } from "../..";
import { DRIVES_ASSET_DATA } from "./assets";
import { DRIVES_CHECK_VALVE_DATA } from "./check-valves";
import { DRIVES_EXCHANGE_CIRCUIT_DATA } from "./exchange-circuits";
import { DRIVES_FLOW_CONTROL_VALVE_DATA } from "./flow-control-valves";
import { DRIVES_FLOW_SENSOR_DATA } from "./flow-sensors";
import { DRIVES_HEAT_EXCHANGER_DATA } from "./heat-exchangers";
import { DRIVES_MANUAL_VALVE_DATA } from "./manual-valves";
import { DRIVES_MIX_VALVE_DATA } from "./mix-valves";
import { DRIVES_PRESSURE_GAUGE_DATA } from "./pressure-gauges";
import { DRIVES_PRESSURE_SENSOR_DATA } from "./pressure-sensors";
import { DRIVES_PUMP_DATA } from "./pumps";
import { DRIVES_SWITCH_VALVE_DATA } from "./switch-valves";
import { DRIVES_TEMPERATURE_SENSOR_DATA } from "./temperature-sensors";

export { DRIVES_ASSET_DATA } from "./assets";
export { DRIVES_CHECK_VALVE_DATA } from "./check-valves";
export { DRIVES_EXCHANGE_CIRCUIT_DATA } from "./exchange-circuits";
export { DRIVES_FLOW_CONTROL_VALVE_DATA } from "./flow-control-valves";
export { DRIVES_FLOW_SENSOR_DATA } from "./flow-sensors";
export { DRIVES_HEAT_EXCHANGER_DATA } from "./heat-exchangers";
export { DRIVES_MANUAL_VALVE_DATA } from "./manual-valves";
export { DRIVES_MIX_VALVE_DATA } from "./mix-valves";
export { DRIVES_PRESSURE_GAUGE_DATA } from "./pressure-gauges";
export { DRIVES_PRESSURE_SENSOR_DATA } from "./pressure-sensors";
export { DRIVES_PUMP_DATA } from "./pumps";
export { DRIVES_SWITCH_VALVE_DATA } from "./switch-valves";
export { DRIVES_TEMPERATURE_SENSOR_DATA } from "./temperature-sensors";

export const DRIVES_MIMIC_DATA = toFieldsMap({
  ...DRIVES_ASSET_DATA,
  ...DRIVES_CHECK_VALVE_DATA,
  ...DRIVES_EXCHANGE_CIRCUIT_DATA,
  ...DRIVES_FLOW_CONTROL_VALVE_DATA,
  ...DRIVES_FLOW_SENSOR_DATA,
  ...DRIVES_HEAT_EXCHANGER_DATA,
  ...DRIVES_MANUAL_VALVE_DATA,
  ...DRIVES_MIX_VALVE_DATA,
  ...DRIVES_PRESSURE_GAUGE_DATA,
  ...DRIVES_PRESSURE_SENSOR_DATA,
  ...DRIVES_PUMP_DATA,
  ...DRIVES_SWITCH_VALVE_DATA,
  ...DRIVES_TEMPERATURE_SENSOR_DATA,
});
