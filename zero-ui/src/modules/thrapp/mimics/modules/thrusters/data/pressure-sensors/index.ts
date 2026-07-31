import { toFieldsMap } from "../../..";
import { MimicComponentType } from "../../../../../types";
import _1095_01 from "./_1095_01";
import _1097_01 from "./_1097_01";
import _1097_02 from "./_1097_02";

export const THRUSTERS_PRESSURE_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.PressureSensor]: {
    "1097-01": _1097_01,
    "1097-02": _1097_02,
  },
  [MimicComponentType.PressureGauge]: {
    "1095-01": _1095_01,
  },
});
