import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { controllerState, controls, measurement, parameters, tooltip } from "./shared";

export default toInstance<MimicComponentType.TemperatureSensor>({
  controls,
  controllerState,
  custom: {},
  parameters,
  source: measurement,
  sensors: {
    measurement,
  },
  tooltip: tooltip({
    yardTag: "1038-65",
    technicalName: "dhw-temperature-boosting-supply",
  }),
});
