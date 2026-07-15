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
    valve: getField(ControlComponentType.Valve, "dhw", "dhwFlowcontrolDc"),
  },
  controllerState: {
    controller: getField(ControllerStateComponentType.PIDController, "dhw", "dhwDcFlowController"),
  },
  custom: {},
  parameters: {
    flow: getField(ParametersType.FlowControl, "dhw", "dcFlowcontrolMinimumSetpoint"),
  },
  source: getField(SensorComponentType.Valve, "dhw", "dhwFlowcontrolDc"),
  sensors: {
    measurement: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureDrivesReturn"),
  },
  tooltip: tooltip({
    yardTag: "1064-03",
    technicalName: "dhw-flowcontrol-dc",
  }),
});
