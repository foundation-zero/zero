import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { pump, tooltip } from "./shared";

export default toInstance<MimicComponentType.FlowSensor>({
  controls: {
    pump,
    controller: getField(
      ControlComponentType.PIDController,
      "boilers",
      "boilersPumpFlowController",
    ),
  },
  custom: {},
  parameters: {
    flow: getField(ParametersType.Flow, "boilers", "heatpumpFlowSetpoint"),
  },
  source: getField(SensorComponentType.Flow, "boilers", "boilersFlowBoosting"),
  sensors: {
    temperature: getField(
      SensorComponentType.Temperature,
      "boilers",
      "boilersTemperatureBoostingReturn",
    ),
  },
  tooltip: tooltip({
    yardTag: "1058-11",
    technicalName: "boilers-flow-boosting",
  }),
});
