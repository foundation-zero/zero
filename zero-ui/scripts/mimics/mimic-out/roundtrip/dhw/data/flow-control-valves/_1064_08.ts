import { ControlComponentType, SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
import { drivesFlowController } from "../controllers";
export default toInstance<MimicComponentType.FlowControlValve>({
  custom: {
    controller: drivesFlowController,
  },
  controls: {
    valve: getField(ControlComponentType.Valve, "dhw", "dhwFlowcontrolDrives"),
  },
  controllerState: {},
  parameters: {},
  source: getField(SensorComponentType.Valve, "dhw", "dhwFlowcontrolDrives"),
  sensors: {},
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Flow control valve",
      componentType: "Flow control valve DN 20",
    });
  },
});
