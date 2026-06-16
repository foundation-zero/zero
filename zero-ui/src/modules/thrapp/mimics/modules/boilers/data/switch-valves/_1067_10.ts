import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";

import { tank2, tooltip, toSwitchValve } from ".";
import { getField } from "../../../../providers";

export default toSwitchValve({
  controls: {
    valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchTank2BoostingSupply"),
  },
  custom: { tank: tank2 },
  parameters: {},
  sensors: {
    valve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank2BoostingSupply"),
  },
  tooltip: tooltip({
    yardTag: "1067-10",
    technicalName: "boilers-switch-tank-2-boosting-supply",
  }),
});
