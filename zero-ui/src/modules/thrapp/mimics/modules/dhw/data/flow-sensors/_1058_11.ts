import { ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { pumpFlowController } from "../controllers";
import { pump, tooltip } from "./shared";

export default toInstance<MimicComponentType.FlowSensor>({
  controls: {
    pump,
  },
  controllerState: {},
  custom: {
    controller: pumpFlowController,
  },
  parameters: {
    flow: getField(ParametersType.Flow, "dhw", "heatpumpFlowSetpoint"),
  },
  source: getField(SensorComponentType.Flow, "dhw", "dhwFlowBoosting"),
  sensors: {
    temperature: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureBoostingReturn"),
  },
  get tooltip() {
    return tooltip(this.source);
  },
});
