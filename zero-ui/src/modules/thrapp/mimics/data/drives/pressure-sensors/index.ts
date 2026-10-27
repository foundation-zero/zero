import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { toFieldsMap } from "../../../modules";
import { getField } from "../../../providers";
import { toPressureSensor } from "../../helpers";

export const DRIVES_PRESSURE_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.PressureSensor]: {
    "1097-10": toPressureSensor({
      source: getField(SensorComponentType.Pressure, "drives", "drivesPressure"),
    }),
  },
});
