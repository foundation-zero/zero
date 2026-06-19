import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { controls, measurement, parameters, tooltip } from "./shared";

export default toInstance<MimicComponentType.TemperatureSensor>({
  controls,
  custom: {},
  parameters,
  source: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureBoostingReturn"),
  sensors: {
    measurement,
  },
  tooltip: tooltip({
    yardTag: "1038-66",
    technicalName: "dhw-temperature-boosting-return",
  }),
});
