import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { controls, measurement, parameters, tooltip } from "./shared";

export default toInstance<MimicComponentType.TemperatureSensor>({
  controls,
  custom: {},
  parameters,
  source: getField(SensorComponentType.Temperature, "boilers", "boilersTemperatureLt2Return"),
  sensors: {
    measurement,
  },
  tooltip: tooltip({
    yardTag: "1038-26",
    technicalName: "boilers-temperature-lt2-return",
  }),
});
