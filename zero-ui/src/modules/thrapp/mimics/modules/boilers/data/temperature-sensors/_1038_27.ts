import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.TemperatureSensor>({
  controls: {},
  custom: {},
  parameters: {},
  sensors: {
    temperature: getField(SensorComponentType.Temperature, "boilers", "boilersTemperatureTank3"),
  },
  tooltip: tooltip({
    yardTag: "1038-27",
    technicalName: "boilers-temperature-tank-3",
  }),
});
