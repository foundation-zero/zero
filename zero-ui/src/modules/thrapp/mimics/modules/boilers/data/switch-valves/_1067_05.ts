import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";

import { tank3, tooltip, toSwitchValve } from ".";
import { getField } from "../../../../providers";

export default toSwitchValve({
  controls: {
    valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchTank3Empty"),
  },
  custom: { tank: tank3 },
  parameters: {},
  sensors: {
    valve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank3Empty"),
  },
  tooltip: tooltip({
    yardTag: "1067-05",
    technicalName: "boilers-switch-tank-3-empty",
  }),
});
