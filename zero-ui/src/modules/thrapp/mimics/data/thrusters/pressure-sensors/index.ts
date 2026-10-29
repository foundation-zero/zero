import { MimicComponentType } from "../../../../types";
import { toFieldsMap } from "../../../modules";
import { toPressureGauge } from "../../helpers";
import _1097_01 from "./_1097_01";
import _1097_02 from "./_1097_02";
import _1097_06 from "./_1097_06";

export const THRUSTERS_PRESSURE_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.PressureSensor]: {
    "1097-01": _1097_01,
    "1097-02": _1097_02,
    "1097-06": _1097_06,
  },
  [MimicComponentType.PressureGauge]: {
    "1095-01": toPressureGauge("1095-01"),
  },
});
