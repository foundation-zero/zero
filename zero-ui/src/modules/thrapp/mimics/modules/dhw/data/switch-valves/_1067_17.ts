import { ControlComponentType, SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.SwitchValve>({
  controls: {
    valve: getField(ControlComponentType.Valve, "dhw", "dhwSwitchHeatpump"),
  },
  controllerState: {},
  custom: {},
  parameters: {},
  source: getField(SensorComponentType.Valve, "dhw", "dhwSwitchHeatpump"),
  sensors: {},
  get tooltip() {
    return tooltip(this.source);
  },
});
