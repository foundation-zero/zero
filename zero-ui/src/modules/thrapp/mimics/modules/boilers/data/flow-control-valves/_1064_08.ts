import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { actuator, tooltip } from "./shared";

export default toInstance<MimicComponentType.FlowControlValve>({
  controls: {
    valve: getField(ControlComponentType.Valve, "boilers", "boilersFlowcontrolLt1"),
    controller: getField(ControlComponentType.PIDController, "boilers", "boilersLt1FlowController"),
    pump: actuator,
  },
  custom: {
    controllerName: "LT1_flow_controller",
  },
  parameters: {
    flow: getField(ParametersType.Flow, "boilers", "lt1FlowcontrolMinimumSetpoint"),
  },
  source: getField(SensorComponentType.Valve, "boilers", "boilersFlowcontrolLt1"),
  sensors: {
    measurement: getField(SensorComponentType.Flow, "boilers", "boilersFlowLt1"),
  },
  tooltip: tooltip({
    yardTag: "1064-08",
    technicalName: "boilers-flowcontrol-lt1",
  }),
});
