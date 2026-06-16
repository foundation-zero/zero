import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";

import { tank1, tooltip, toSwitchValve } from ".";
import { getField } from "../../../../providers";

export default toSwitchValve({
  controls: {
    valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchTank1Empty"),
  },
  custom: { tank: tank1 },
  parameters: {},
  sensors: {
    valve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank1Empty"),
  },
  tooltip: tooltip({
    yardTag: "1067-13",
    technicalName: "boilers-switch-tank-1-empty",
  }),
});
