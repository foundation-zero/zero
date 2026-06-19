import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.SwitchValve>({
  controls: {
    valve: getField(ControlComponentType.Valve, "dhw", "dhwSwitchLowTemperature"),
  },
  custom: {},
  parameters: {},
  source: getField(SensorComponentType.Valve, "dhw", "dhwSwitchLowTemperature"),
  sensors: {},
  tooltip: tooltip({
    yardTag: "1067-16",
    technicalName: "dhw-switch-low-temperature",
  }),
});
