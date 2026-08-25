import { ControlComponentType, ControllerStateComponentType, ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
export default toInstance<MimicComponentType.FlowControlValve>({
  custom: {},
  controls: {
    valve: getField(ControlComponentType.Valve, "thrusters", "thrustersFlowcontrolFwd"),
  },
  controllerState: {
    controller: getField(ControllerStateComponentType.PIDController, "thrusters", "thrustersFwdFlowController"),
  },
  parameters: {
    flow: getField(ParametersType.Tuning, "thrusters", "fwdFlowBalanceTuning"),
  },
  source: getField(SensorComponentType.Valve, "thrusters", "thrustersFlowcontrolFwd"),
  sensors: {
    measurement: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowFwd"),
  },
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Flow Control valve",
      componentType: "2 way valve DN 25",
    });
  },
});
