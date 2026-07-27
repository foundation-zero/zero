import { toFieldsMap } from "../..";
import { THRUSTERS_ASSET_DATA } from "./assets";
import { THRUSTERS_CHECK_VALVE_DATA } from "./check-valves";
import { THRUSTERS_EXCHANGE_CIRCUIT_DATA } from "./exchange-circuits";
import { THRUSTERS_FLOW_CONTROL_VALVE_DATA } from "./flow-control-valves";
import { THRUSTERS_FLOW_SENSOR_DATA } from "./flow-sensors";
import { THRUSTERS_HEAT_EXCHANGER_DATA } from "./heat-exchangers";
import { THRUSTERS_MANUAL_VALVE_DATA } from "./manual-valves";
import { THRUSTERS_MIX_VALVE_DATA } from "./mix-valves";
import { THRUSTERS_PRESSURE_SENSOR_DATA } from "./pressure-sensors";
import { THRUSTERS_PUMP_DATA } from "./pumps";
import { THRUSTERS_SWITCH_VALVE_DATA } from "./switch-valves";
import { THRUSTERS_TEMPERATURE_SENSOR_DATA } from "./temperature-sensors";

export { THRUSTERS_ASSET_DATA } from "./assets";
export { THRUSTERS_CHECK_VALVE_DATA } from "./check-valves";
export { THRUSTERS_EXCHANGE_CIRCUIT_DATA } from "./exchange-circuits";
export { THRUSTERS_FLOW_CONTROL_VALVE_DATA } from "./flow-control-valves";
export { THRUSTERS_FLOW_SENSOR_DATA } from "./flow-sensors";
export { THRUSTERS_HEAT_EXCHANGER_DATA } from "./heat-exchangers";
export { THRUSTERS_MANUAL_VALVE_DATA } from "./manual-valves";
export { THRUSTERS_MIX_VALVE_DATA } from "./mix-valves";
export { THRUSTERS_PRESSURE_SENSOR_DATA } from "./pressure-sensors";
export { THRUSTERS_PUMP_DATA } from "./pumps";
export { THRUSTERS_SWITCH_VALVE_DATA } from "./switch-valves";
export { THRUSTERS_TEMPERATURE_SENSOR_DATA } from "./temperature-sensors";

export const THRUSTERS_MIMIC_DATA = toFieldsMap({
  ...THRUSTERS_HEAT_EXCHANGER_DATA,
  ...THRUSTERS_SWITCH_VALVE_DATA,
  ...THRUSTERS_FLOW_CONTROL_VALVE_DATA,
  ...THRUSTERS_PUMP_DATA,
  ...THRUSTERS_MANUAL_VALVE_DATA,
  ...THRUSTERS_MIX_VALVE_DATA,
  ...THRUSTERS_PRESSURE_SENSOR_DATA,
  ...THRUSTERS_FLOW_SENSOR_DATA,
  ...THRUSTERS_TEMPERATURE_SENSOR_DATA,
  ...THRUSTERS_CHECK_VALVE_DATA,
  ...THRUSTERS_EXCHANGE_CIRCUIT_DATA,
  ...THRUSTERS_ASSET_DATA,
});
