import { MimicComponentType } from "../../../../types";
import { toFieldsMap } from "../../../modules";
import { toPressureGauge } from "../../helpers";
import _1097_11 from "./_1097_11";

export const DHW_PRESSURE_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.PressureSensor]: {
    "1097-11": _1097_11,
  },
  [MimicComponentType.PressureGauge]: {
    "1095-14": toPressureGauge("1095-14"),
  },
});
