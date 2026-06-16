import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";

import { tank2, tooltip, toSwitchValve } from ".";
import { getField } from "../../../../providers";

export default toSwitchValve({
  controls: {
    valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchTank2BoostingReturn"),
  },
  custom: { tank: tank2 },
  parameters: {},
  sensors: {
    valve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank2BoostingReturn"),
  },
  tooltip: tooltip({
    yardTag: "1067-08",
    technicalName: "boilers-switch-tank-2-boosting-return",
  }),
});
