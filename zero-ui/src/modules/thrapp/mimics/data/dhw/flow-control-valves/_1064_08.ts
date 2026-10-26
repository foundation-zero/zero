import { ControlComponentType, SensorComponentType } from "@/modules/thrsim/types";
import { toFlowControlValve } from "../../helpers";

import { getField } from "../../../providers";
import { drivesFlowController } from "../controllers";

export default toFlowControlValve(
  {
    controls: {
      valve: getField(ControlComponentType.Valve, "dhw", "dhwFlowcontrolDrives"),
    },
    custom: {
      controller: drivesFlowController,
    },
    source: getField(SensorComponentType.Valve, "dhw", "dhwFlowcontrolDrives"),
  },
  { componentType: "Flow control valve DN 20" },
);
