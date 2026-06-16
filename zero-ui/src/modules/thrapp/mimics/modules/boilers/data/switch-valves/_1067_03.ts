import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";

import { tank3, tooltip, toSwitchValve } from ".";
import { getField } from "../../../../providers";

export default toSwitchValve({
  controls: {
    valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchTank3Fill"),
  },
  custom: { tank: tank3 },
  parameters: {},
  sensors: {
    valve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank3Fill"),
  },
  tooltip: tooltip({
    yardTag: "1067-03",
    technicalName: "boilers-switch-tank-3-fill",
  }),
});
