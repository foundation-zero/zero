import {
  ControlComponentType,
  ControllerStateComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrsim/types";
import { toFlowControlValve } from "../../helpers";

import { getField } from "../../../providers";

export default toFlowControlValve(
  {
    controls: {
      valve: getField(ControlComponentType.Valve, "thrusters", "thrustersFlowcontrolAft"),
    },
    controllerState: {
      controller: getField(
        ControllerStateComponentType.PIDController,
        "thrusters",
        "thrustersAftFlowController",
      ),
    },
    parameters: {
      flow: getField(ParametersType.Tuning, "thrusters", "aftFlowBalanceTuning"),
    },
    source: getField(SensorComponentType.Valve, "thrusters", "thrustersFlowcontrolAft"),
    sensors: {
      measurement: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowAft"),
    },
  },
  { title: "Flow Control valve" },
);
