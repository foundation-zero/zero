import {
  ControllerStateComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { pump, tooltip } from "./shared";

export default toInstance<MimicComponentType.FlowSensor>({
  controls: {
    pump,
  },
  controllerState: {
    controller: getField(
      ControllerStateComponentType.PIDController,
      "dhw",
      "dhwDrivesFlowController",
    ),
  },
  custom: {},
  parameters: {
    flow: getField(ParametersType.FlowControl, "dhw", "drivesFlowcontrolMinimumSetpoint"),
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
