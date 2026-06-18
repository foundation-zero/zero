import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { controls, measurement, parameters, tooltip } from "./shared";

export default toInstance<MimicComponentType.TemperatureSensor>({
  controls,
  custom: {},
  parameters,
  sensors: {
    temperature: measurement,
    measurement,
  },
  tooltip: tooltip({
    yardTag: "1038-65",
    technicalName: "boilers-temperature-boosting-supply",
  }),
});
