import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.SwitchValve>({
  controls: {
    valve: getField(ControlComponentType.Valve, "dhw", "dhwSwitchHeatpump"),
  },
  custom: {},
  parameters: {},
  source: getField(SensorComponentType.Valve, "dhw", "dhwSwitchHeatpump"),
  sensors: {},
  tooltip: tooltip({
    yardTag: "1067-17",
    technicalName: "dhw-switch-heatpump",
  }),
});
