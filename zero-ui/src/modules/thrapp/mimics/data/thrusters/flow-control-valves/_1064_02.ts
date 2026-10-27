import {
  ControlComponentType,
  ControllerStateComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrapp/types/thrs";
import { toFlowControlValve } from "../../helpers";

import { getField } from "../../../providers";

export default toFlowControlValve(
  {
    controls: {
      valve: getField(ControlComponentType.Valve, "thrusters", "thrustersFlowcontrolFwd"),
    },
    controllerState: {
      controller: getField(
        ControllerStateComponentType.PIDController,
        "thrusters",
        "thrustersFwdFlowController",
      ),
    },
    parameters: {
      flow: getField(ParametersType.Tuning, "thrusters", "fwdFlowBalanceTuning"),
    },
    source: getField(SensorComponentType.Valve, "thrusters", "thrustersFlowcontrolFwd"),
    sensors: {
      measurement: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowFwd"),
    },
  },
  { title: "Flow Control valve" },
);
