import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { pumpTemperatureController } from "../controllers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.TemperatureSensor>({
  controls: {},
  controllerState: {},
  custom: { controller: pumpTemperatureController },
  parameters: {},
  source: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureBoostingReturn"),
  sensors: {},
  tooltip: tooltip({
    yardTag: "1038-66",
    technicalName: "dhw-temperature-boosting-return",
  }),
});
