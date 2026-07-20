import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.TemperatureSensor>({
  controls: {},
  controllerState: {},
  custom: {},
  parameters: {},
  source: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureTank3"),
  sensors: {},
  tooltip: tooltip({
    yardTag: "1038-27",
    technicalName: "dhw-temperature-tank-3",
  }),
});
