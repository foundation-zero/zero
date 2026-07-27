import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.SwitchValve>({
  controls: {
    valve: getField(ControlComponentType.Valve, "dhw", "dhwSwitchHighTemperature"),
  },
  controllerState: {},
  custom: {},
  parameters: {},
  source: getField(SensorComponentType.Valve, "dhw", "dhwSwitchHighTemperature"),
  sensors: {},
  get tooltip() {
    return tooltip(this.source);
  },
});
