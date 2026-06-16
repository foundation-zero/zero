import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";

import { tank2, tooltip, toSwitchValve } from ".";
import { getField } from "../../../../providers";

export default toSwitchValve({
  controls: {
    valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchTank2Fill"),
  },
  custom: { tank: tank2 },
  parameters: {},
  sensors: {
    valve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank2Fill"),
  },
  tooltip: tooltip({
    yardTag: "1067-07",
    technicalName: "boilers-switch-tank-2-fill",
  }),
});
