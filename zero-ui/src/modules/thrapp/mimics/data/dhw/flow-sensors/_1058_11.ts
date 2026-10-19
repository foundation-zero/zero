import { ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { toFlowSensor } from "../../helpers";

import { getField } from "../../../providers";
import { pumpFlowController } from "../controllers";
import { pump } from "./shared";

export default toFlowSensor({
  controls: {
    pump,
  },
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
});
