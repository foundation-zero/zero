import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { controllerState, parameters, tooltip } from "./shared";

export default toInstance<MimicComponentType.TemperatureSensor>({
  controls: {},
  controllerState,
  custom: {},
  parameters,
  source: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureTank2"),
  sensors: {},
  tooltip: tooltip({
    yardTag: "1038-44",
    technicalName: "dhw-temperature-tank-2",
  }),
});
