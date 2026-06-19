import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { tank1, tooltip } from "./shared";

export default toInstance<MimicComponentType.SwitchValve>({
  controls: {
    valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchTank1Fill"),
  },
  custom: { tank: tank1 },
  parameters: {},
  source: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank1Fill"),
  sensors: {},
  tooltip: tooltip({
    yardTag: "1067-11",
    technicalName: "boilers-switch-tank-1-fill",
  }),
});
