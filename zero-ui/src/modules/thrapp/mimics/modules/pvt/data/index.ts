import { toFieldsMap } from "../..";
import { PVT_ASSET_DATA } from "./assets";
import { PVT_CHECK_VALVE_DATA } from "./check-valves";
import { PVT_EXCHANGE_CIRCUIT_DATA } from "./exchange-circuits";
import { PVT_FLOW_SENSOR_DATA } from "./flow-sensors";
import { PVT_HEAT_EXCHANGER_DATA } from "./heat-exchangers";
import { PVT_MANUAL_VALVE_DATA } from "./manual-valves";
import { PVT_MIX_VALVE_DATA } from "./mix-valves";
import { PVT_PRESSURE_GAUGE_DATA } from "./pressure-gauges";
import { PVT_PRESSURE_SENSOR_DATA } from "./pressure-sensors";
import { PVT_PUMP_DATA } from "./pumps";
import { PVT_SWITCH_VALVE_DATA } from "./switch-valves";
import { PVT_TEMPERATURE_SENSOR_DATA } from "./temperature-sensors";

export { PVT_ASSET_DATA } from "./assets";
export { PVT_CHECK_VALVE_DATA } from "./check-valves";
export { PVT_EXCHANGE_CIRCUIT_DATA } from "./exchange-circuits";
export { PVT_FLOW_SENSOR_DATA } from "./flow-sensors";
export { PVT_HEAT_EXCHANGER_DATA } from "./heat-exchangers";
export { PVT_MANUAL_VALVE_DATA } from "./manual-valves";
export { PVT_MIX_VALVE_DATA } from "./mix-valves";
export { PVT_PRESSURE_GAUGE_DATA } from "./pressure-gauges";
export { PVT_PRESSURE_SENSOR_DATA } from "./pressure-sensors";
export { PVT_PUMP_DATA } from "./pumps";
export { PVT_SWITCH_VALVE_DATA } from "./switch-valves";
export { PVT_TEMPERATURE_SENSOR_DATA } from "./temperature-sensors";

export const PVT_MIMIC_DATA = toFieldsMap({
  ...PVT_SWITCH_VALVE_DATA,
  ...PVT_MIX_VALVE_DATA,
  ...PVT_CHECK_VALVE_DATA,
  ...PVT_PUMP_DATA,
  ...PVT_MANUAL_VALVE_DATA,
  ...PVT_PRESSURE_SENSOR_DATA,
  ...PVT_PRESSURE_GAUGE_DATA,
  ...PVT_FLOW_SENSOR_DATA,
  ...PVT_TEMPERATURE_SENSOR_DATA,
  ...PVT_EXCHANGE_CIRCUIT_DATA,
  ...PVT_ASSET_DATA,
  ...PVT_HEAT_EXCHANGER_DATA,
});
