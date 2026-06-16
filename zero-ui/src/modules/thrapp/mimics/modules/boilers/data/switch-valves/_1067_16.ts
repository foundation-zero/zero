import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";

import { tooltip, toSwitchValve } from ".";
import { getField } from "../../../../providers";

export default toSwitchValve({
  controls: {
    valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchLowTemperature"),
  },
  custom: {},
  parameters: {},
  sensors: {
    valve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchLowTemperature"),
  },
  tooltip: tooltip({
    yardTag: "1067-16",
    technicalName: "boilers-switch-low-temperature",
  }),
});
