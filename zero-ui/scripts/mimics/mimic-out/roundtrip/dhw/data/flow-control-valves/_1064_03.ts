import { ControlComponentType, SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
import { dcFlowController } from "../controllers";
export default toInstance<MimicComponentType.FlowControlValve>({
  custom: {
    controller: dcFlowController,
  },
  controls: {
    valve: getField(ControlComponentType.Valve, "dhw", "dhwFlowcontrolDc"),
  },
  controllerState: {},
  parameters: {},
  source: getField(SensorComponentType.Valve, "dhw", "dhwFlowcontrolDc"),
  sensors: {},
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Flow control valve",
      componentType: "Flow control valve DN 20",
    });
  },
});
