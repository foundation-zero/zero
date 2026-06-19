import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { tank2, tooltip } from "./shared";

export default toInstance<MimicComponentType.SwitchValve>({
  controls: {
    valve: getField(ControlComponentType.Valve, "dhw", "dhwSwitchTank2BoostingReturn"),
  },
  custom: { tank: tank2 },
  parameters: {},
  source: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank2BoostingReturn"),
  sensors: {},
  tooltip: tooltip({
    yardTag: "1067-08",
    technicalName: "dhw-switch-tank-2-boosting-return",
  }),
});
