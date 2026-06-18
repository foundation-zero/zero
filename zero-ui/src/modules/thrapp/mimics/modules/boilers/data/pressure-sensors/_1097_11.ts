import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { controls, flow, parameters, tooltip } from "./shared";

export default toInstance<MimicComponentType.PressureSensor>({
  controls,
  custom: {},
  parameters,
  sensors: {
    pressure: getField(SensorComponentType.Pressure, "boilers", "boilersPressureBoosting"),
    flow,
  },
  tooltip: tooltip({
    yardTag: "1097-11",
    technicalName: "boilers-pressure-boosting",
  }),
});
