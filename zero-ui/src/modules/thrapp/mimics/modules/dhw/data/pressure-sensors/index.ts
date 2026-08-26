import { toFieldsMap } from "../../..";
import { MimicComponentType } from "../../../../../types";
import _1095_14 from "./_1095_14";
import _1097_11 from "./_1097_11";

export const DHW_PRESSURE_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.PressureSensor]: {
    "1097-11": _1097_11,
  },
  [MimicComponentType.PressureGauge]: {
    "1095-14": _1095_14,
  },
});
