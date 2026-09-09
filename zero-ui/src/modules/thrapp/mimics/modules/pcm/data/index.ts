import { toFieldsMap } from "../..";
import { DHW_EXCHANGE_CIRCUIT_DATA, DHW_HEAT_EXCHANGER_DATA } from "../../dhw/data";
import { PCM_CHECK_VALVE_DATA } from "./check-valves";
import { PCM_CONNECTING_CIRCUIT_DATA } from "./connecting-circuits";
import { PCM_FLOW_CONTROL_VALVE_DATA } from "./flow-control-valves";
import { PCM_FLOW_SENSOR_DATA } from "./flow-sensors";
import { PCM_HEAT_BATTERIES_DATA } from "./heat-batteries";
import { PCM_MANUAL_VALVE_DATA } from "./manual-valves";
import { PCM_PRESSURE_GAUGE_DATA } from "./pressure-gauges";
import { PCM_PUMP_DATA } from "./pumps";
import { PCM_SWITCH_VALVE_DATA } from "./switch-valves";
import { PCM_TEMPERATURE_SENSOR_DATA } from "./temperature-sensors";

export { PCM_TEMPERATURE_SENSOR_DATA } from "./temperature-sensors";

export const PCM_MIMIC_DATA = toFieldsMap({
  ...PCM_CONNECTING_CIRCUIT_DATA,
  ...PCM_FLOW_SENSOR_DATA,
  ...PCM_FLOW_CONTROL_VALVE_DATA,
  ...DHW_EXCHANGE_CIRCUIT_DATA,
  ...DHW_HEAT_EXCHANGER_DATA,
  ...PCM_HEAT_BATTERIES_DATA,
  ...PCM_SWITCH_VALVE_DATA,
  ...PCM_MANUAL_VALVE_DATA,
  ...PCM_PUMP_DATA,
  ...PCM_CHECK_VALVE_DATA,
  ...PCM_PRESSURE_GAUGE_DATA,
  ...PCM_TEMPERATURE_SENSOR_DATA,
});
