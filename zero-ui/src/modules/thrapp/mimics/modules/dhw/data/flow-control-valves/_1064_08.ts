import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { drivesFlowController } from "../controllers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.FlowControlValve>({
  controls: {
    valve: getField(ControlComponentType.Valve, "dhw", "dhwFlowcontrolDrives"),
  },
  controllerState: {},
  custom: {
    controller: drivesFlowController,
  },
  parameters: {},
  source: getField(SensorComponentType.Valve, "dhw", "dhwFlowcontrolDrives"),
  sensors: {},
  get tooltip() {
    return tooltip(this.source);
  },
});
