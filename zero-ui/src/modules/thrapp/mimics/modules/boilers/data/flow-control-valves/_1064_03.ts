import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { actuator, tooltip } from "./shared";

export default toInstance<MimicComponentType.FlowControlValve>({
  controls: {
    valve: getField(ControlComponentType.Valve, "boilers", "boilersFlowcontrolLt2"),
    controller: getField(ControlComponentType.PIDController, "boilers", "boilersLt2FlowController"),
    pump: actuator,
  },
  custom: {},
  parameters: {
    flow: getField(ParametersType.Flow, "boilers", "lt2FlowcontrolMinimumSetpoint"),
  },
  source: getField(SensorComponentType.Valve, "boilers", "boilersFlowcontrolLt2"),
  sensors: {
    measurement: getField(SensorComponentType.Flow, "boilers", "boilersFlowLt2"),
  },
  tooltip: tooltip({
    yardTag: "1064-03",
    technicalName: "boilers-flowcontrol-lt2",
  }),
});
