import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";

import { tank3, tooltip, toSwitchValve } from ".";
import { getField } from "../../../../providers";

export default toSwitchValve({
  controls: {
    valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchTank3BoostingReturn"),
  },
  custom: { tank: tank3 },
  parameters: {},
  sensors: {
    valve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank3BoostingReturn"),
  },
  tooltip: tooltip({
    yardTag: "1067-04",
    technicalName: "boilers-switch-tank-3-boosting-return",
  }),
});
