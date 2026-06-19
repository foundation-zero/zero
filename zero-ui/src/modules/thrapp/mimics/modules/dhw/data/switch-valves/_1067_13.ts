import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { tank1, tooltip } from "./shared";

export default toInstance<MimicComponentType.SwitchValve>({
  controls: {
    valve: getField(ControlComponentType.Valve, "dhw", "dhwSwitchTank1Outlet"),
  },
  custom: { tank: tank1 },
  parameters: {},
  source: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank1Outlet"),
  sensors: {},
  tooltip: tooltip({
    yardTag: "1067-13",
    technicalName: "dhw-switch-tank-1-empty",
  }),
});
