import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";

import { tank1, tooltip, toSwitchValve } from ".";
import { getField } from "../../../../providers";

export default toSwitchValve({
  controls: {
    valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchTank1BoostingSupply"),
  },
  custom: { tank: tank1 },
  parameters: {},
  sensors: {
    valve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank1BoostingSupply"),
  },
  tooltip: tooltip({
    yardTag: "1067-14",
    technicalName: "boilers-switch-tank-1-boosting-supply",
  }),
});
