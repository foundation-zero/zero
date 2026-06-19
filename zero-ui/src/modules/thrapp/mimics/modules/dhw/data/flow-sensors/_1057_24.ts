import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { pump, tooltip } from "./shared";

export default toInstance<MimicComponentType.FlowSensor>({
  controls: {
    pump,
    controller: getField(ControlComponentType.PIDController, "dhw", "dhwDrivesFlowController"),
  },
  custom: {},
  parameters: {
    flow: getField(ParametersType.Flow, "dhw", "drivesFlowcontrolMinimumSetpoint"),
  },
  source: getField(SensorComponentType.Flow, "dhw", "dhwFlowDrives"),
  sensors: {
    temperature: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureFreshwaterSupply"),
  },
  tooltip: tooltip({
    yardTag: "1057-24",
    technicalName: "dhw-flow-drives",
  }),
});
