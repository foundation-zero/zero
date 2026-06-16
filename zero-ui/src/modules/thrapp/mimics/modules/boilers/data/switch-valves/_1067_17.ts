import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";

import { tooltip, toSwitchValve } from ".";
import { getField } from "../../../../providers";

export default toSwitchValve({
  controls: {
    valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchHeatpump"),
  },
  custom: {},
  parameters: {},
  sensors: {
    valve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchHeatpump"),
  },
  tooltip: tooltip({
    yardTag: "1067-17",
    technicalName: "boilers-switch-heatpump",
  }),
});
