import { ControlComponentType, SensorComponentType } from "@/modules/thrapp/types/thrs";
import { toFlowControlValve } from "../../helpers";

import { getField } from "../../../providers";
import { dcFlowController } from "../controllers";

export default toFlowControlValve(
  {
    controls: {
      valve: getField(ControlComponentType.Valve, "dhw", "dhwFlowcontrolDc"),
    },
    custom: {
      controller: dcFlowController,
    },
    source: getField(SensorComponentType.Valve, "dhw", "dhwFlowcontrolDc"),
  },
  { componentType: "Flow control valve DN 20" },
);
