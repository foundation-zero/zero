import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { toFieldsMap } from "../../../modules";
import { getField } from "../../../providers";
import { toPressureSensor } from "../../helpers";

export const DC_PRESSURE_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.PressureSensor]: {
    "1097-07": toPressureSensor({
      source: getField(SensorComponentType.Pressure, "dc", "dcPressureAft"),
    }),
    "1097-08": toPressureSensor({
      source: getField(SensorComponentType.Pressure, "dc", "dcPressureUgrid"),
    }),
    "1097-09": toPressureSensor({
      source: getField(SensorComponentType.Pressure, "dc", "dcPressureFwd"),
    }),
  },
});
