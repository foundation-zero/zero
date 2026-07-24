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
      "dhwPumpFlowController",
    ),
  },
  custom: {},
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
