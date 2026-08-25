import { ControlComponentType, SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
export default toInstance<MimicComponentType.SwitchValve>({
  custom: {},
  controls: {
    valve: getField(ControlComponentType.Valve, "dhw", "dhwSwitchHighTemperature"),
  },
  controllerState: {},
  parameters: {},
  source: getField(SensorComponentType.Valve, "dhw", "dhwSwitchHighTemperature"),
  sensors: {},
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Switch valve",
      componentType: "2 way valve DN 25",
    });
  },
});
