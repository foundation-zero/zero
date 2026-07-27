import {
  ControlComponentType,
  ControllerStateComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.FlowControlValve>({
  controls: {
    valve: getField(ControlComponentType.Valve, "thrusters", "thrustersFlowcontrolFwd"),
  },
  controllerState: {
    controller: getField(
      ControllerStateComponentType.PIDController,
      "thrusters",
      "fwdFlowController",
    ),
  },
  custom: {},
  parameters: {
    flow: getField(ParametersType.Tuning, "thrusters", "fwdFlowBalanceTuning"),
  },
  source: getField(SensorComponentType.Valve, "thrusters", "thrustersFlowcontrolFwd"),
  sensors: {
    measurement: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowFwd"),
  },
  get tooltip() {
    return tooltip(this.source);
  },
});
