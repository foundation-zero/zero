import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { tank3, tooltip } from "./shared";

export default toInstance<MimicComponentType.SwitchValve>({
  controls: {
    valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchTank3BoostingSupply"),
  },
  custom: { tank: tank3 },
  parameters: {},
  source: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank3BoostingSupply"),
  sensors: {},
  tooltip: tooltip({
    yardTag: "1067-06",
    technicalName: "boilers-switch-tank-3-boosting-supply",
  }),
});
