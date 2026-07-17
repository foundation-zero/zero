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
    valve: getField(ControlComponentType.Valve, "thrusters", "thrustersFlowcontrolAft"),
    pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump1"),
  },
  controllerState: {
    controller: getField(
      ControllerStateComponentType.PIDController,
      "thrusters",
      "aftFlowController",
    ),
  },
  custom: {
    controllerName: "aft_flow_controller",
  },
  parameters: {
    flow: getField(ParametersType.FlowControl, "thrusters", "aftFlowcontrolMinimumSetpoint"),
  },
  source: getField(SensorComponentType.Valve, "thrusters", "thrustersFlowcontrolAft"),
  sensors: {
    measurement: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowAft"),
  },
  tooltip: tooltip({
    yardTag: "1064-02",
    technicalName: "thrusters-flowcontrol-aft",
  }),
});
