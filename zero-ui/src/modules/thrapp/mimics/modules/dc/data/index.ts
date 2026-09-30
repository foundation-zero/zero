import { toFieldsMap } from "../..";
import { DC_CHECK_VALVE_DATA } from "./check-valves";
import { DC_CONVERTER_DATA } from "./converters";
import { DC_EXCHANGE_CIRCUIT_DATA } from "./exchange-circuits";
import { DC_FLOW_SENSOR_DATA } from "./flow-sensors";
import { DC_HEAT_EXCHANGER_DATA } from "./heat-exchangers";
import { DC_MANUAL_VALVE_DATA } from "./manual-valves";
import { DC_MIX_VALVE_DATA } from "./mix-valves";
import { DC_PRESSURE_GAUGE_DATA } from "./pressure-gauges";
import { DC_PRESSURE_SENSOR_DATA } from "./pressure-sensors";
import { DC_PUMP_DATA } from "./pumps";
import { DC_TEMPERATURE_SENSOR_DATA } from "./temperature-sensors";

export { DC_CHECK_VALVE_DATA } from "./check-valves";
export { DC_CONVERTER_DATA } from "./converters";
export { DC_EXCHANGE_CIRCUIT_DATA } from "./exchange-circuits";
export { DC_FLOW_SENSOR_DATA } from "./flow-sensors";
export { DC_HEAT_EXCHANGER_DATA } from "./heat-exchangers";
export { DC_MANUAL_VALVE_DATA } from "./manual-valves";
export { DC_MIX_VALVE_DATA } from "./mix-valves";
export { DC_PRESSURE_GAUGE_DATA } from "./pressure-gauges";
export { DC_PRESSURE_SENSOR_DATA } from "./pressure-sensors";
export { DC_PUMP_DATA } from "./pumps";
export { DC_TEMPERATURE_SENSOR_DATA } from "./temperature-sensors";

export const DC_MIMIC_DATA = toFieldsMap({
  ...DC_CONVERTER_DATA,
  ...DC_EXCHANGE_CIRCUIT_DATA,
  ...DC_CHECK_VALVE_DATA,
  ...DC_PRESSURE_GAUGE_DATA,
  ...DC_HEAT_EXCHANGER_DATA,
  ...DC_MANUAL_VALVE_DATA,
  ...DC_TEMPERATURE_SENSOR_DATA,
  ...DC_PRESSURE_SENSOR_DATA,
  ...DC_FLOW_SENSOR_DATA,
  ...DC_PUMP_DATA,
  ...DC_MIX_VALVE_DATA,
});
