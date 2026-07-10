import { toFieldsMap } from "../..";
import { PVT_ASSET_DATA } from "./assets";
import { PVT_EXCHANGE_CIRCUIT_DATA } from "./exchange-circuits";
import { PVT_FLOW_CONTROL_VALVE_DATA } from "./flow-control-valves";
import { PVT_FLOW_SENSOR_DATA } from "./flow-sensors";
import { PVT_MANUAL_VALVE_DATA } from "./manual-valves";
import { PVT_PRESSURE_SENSOR_DATA } from "./pressure-sensors";
import { PVT_PUMP_DATA } from "./pumps";
import { PVT_SWITCH_VALVE_DATA } from "./switch-valves";
import { PVT_TEMPERATURE_SENSOR_DATA } from "./temperature-sensors";

export { PVT_ASSET_DATA } from "./assets";
export { PVT_EXCHANGE_CIRCUIT_DATA } from "./exchange-circuits";
export { PVT_FLOW_CONTROL_VALVE_DATA } from "./flow-control-valves";
export { PVT_FLOW_SENSOR_DATA } from "./flow-sensors";
export { PVT_MANUAL_VALVE_DATA } from "./manual-valves";
export { PVT_PRESSURE_SENSOR_DATA } from "./pressure-sensors";
export { PVT_PUMP_DATA } from "./pumps";
export { PVT_SWITCH_VALVE_DATA } from "./switch-valves";
export { PVT_TEMPERATURE_SENSOR_DATA } from "./temperature-sensors";

export const PVT_MIMIC_DATA = toFieldsMap({
  ...PVT_SWITCH_VALVE_DATA,
  ...PVT_FLOW_CONTROL_VALVE_DATA,
  ...PVT_PUMP_DATA,
  ...PVT_MANUAL_VALVE_DATA,
  ...PVT_PRESSURE_SENSOR_DATA,
  ...PVT_FLOW_SENSOR_DATA,
  ...PVT_TEMPERATURE_SENSOR_DATA,
  ...PVT_EXCHANGE_CIRCUIT_DATA,
  ...PVT_ASSET_DATA,
});
