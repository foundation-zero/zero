import {
  ControlComponentType,
  ControllerStateComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.FlowControlValve>({
  controls: {
    valve: getField(ControlComponentType.Valve, "thrusters", "thrustersFlowcontrolAft"),
  },
  controllerState: {
    controller: getField(
      ControllerStateComponentType.PIDController,
      "thrusters",
      "aftFlowController",
    ),
  },
  custom: {},
  parameters: {
    flow: getField(ParametersType.Tuning, "thrusters", "aftFlowBalanceTuning"),
  },
  source: getField(SensorComponentType.Valve, "thrusters", "thrustersFlowcontrolAft"),
  sensors: {
    measurement: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowAft"),
  },
  get tooltip() {
    return tooltip(this.source);
  },
});
