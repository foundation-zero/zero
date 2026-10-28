import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { getField } from "../../../providers";
import { toPressureSensor } from "../../helpers";

// Pressure sensors drawn in the thrusters design that have no thrsim field yet.
export const THRUSTERS_PLACEHOLDER_PRESSURE_SENSORS = {
  "1057-24": toPressureSensor(
    { source: getField(SensorComponentType.Pressure, "thrusters", "placeholder") },
    { yardTag: "1057-24" },
  ),
  "1097-06": toPressureSensor(
    { source: getField(SensorComponentType.Pressure, "thrusters", "placeholder") },
    { yardTag: "1097-06" },
  ),
};
