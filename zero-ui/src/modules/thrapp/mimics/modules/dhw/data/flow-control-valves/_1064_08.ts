import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { actuator, tooltip } from "./shared";

export default toInstance<MimicComponentType.FlowControlValve>({
  controls: {
    valve: getField(ControlComponentType.Valve, "dhw", "dhwFlowcontrolDrives"),
    controller: getField(ControlComponentType.PIDController, "dhw", "dhwDrivesFlowController"),
    pump: actuator,
  },
  custom: {
    controllerName: "drives_flow_controller",
  },
  parameters: {
    flow: getField(ParametersType.Flow, "dhw", "drivesFlowcontrolMinimumSetpoint"),
  },
  source: getField(SensorComponentType.Valve, "dhw", "dhwFlowcontrolDrives"),
  sensors: {
    measurement: getField(SensorComponentType.Flow, "dhw", "dhwFlowDrives"),
  },
  tooltip: tooltip({
    yardTag: "1064-08",
    technicalName: "dhw-flowcontrol-drives",
  }),
});
