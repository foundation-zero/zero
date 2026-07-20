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
    flow: getField(ParametersType.Tuning, "thrusters", "fwdFlowBalanceTuning"),
  },
  source: getField(SensorComponentType.Valve, "thrusters", "thrustersFlowcontrolAft"),
  sensors: {
    measurement: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowAft"),
  },
  tooltip: tooltip({
    yardTag: "1064-03",
    technicalName: "thrusters-flowcontrol-dc",
  }),
});
