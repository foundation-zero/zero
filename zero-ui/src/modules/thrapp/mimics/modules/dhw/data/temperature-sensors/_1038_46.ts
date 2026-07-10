import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { controllerState, controls, measurement, parameters, tooltip } from "./shared";

export default toInstance<MimicComponentType.TemperatureSensor>({
  controls,
  controllerState,
  custom: {},
  parameters,
  source: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureDrivesReturn"),
  sensors: {
    measurement,
  },
  tooltip: tooltip({
    yardTag: "1038-46",
    technicalName: "dhw-temperature-drives-return",
  }),
});
