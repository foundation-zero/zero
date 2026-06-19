import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.SwitchValve>({
  controls: {
    valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchHighTemperature"),
  },
  custom: {},
  parameters: {},
  source: getField(SensorComponentType.Valve, "boilers", "boilersSwitchHighTemperature"),
  sensors: {},
  tooltip: tooltip({
    yardTag: "1067-18",
    technicalName: "boilers-switch-high-temperature",
  }),
});
