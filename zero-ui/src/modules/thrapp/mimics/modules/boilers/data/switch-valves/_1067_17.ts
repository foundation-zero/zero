import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.SwitchValve>({
  controls: {
    valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchHeatpump"),
  },
  custom: {},
  parameters: {},
  source: getField(SensorComponentType.Valve, "boilers", "boilersSwitchHeatpump"),
  sensors: {},
  tooltip: tooltip({
    yardTag: "1067-17",
    technicalName: "boilers-switch-heatpump",
  }),
});
