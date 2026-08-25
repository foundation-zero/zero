import { ControlComponentType, ControllerStateComponentType, ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
export default toInstance<MimicComponentType.FlowSensor>({
  custom: {},
  controls: {
    pump: getField(ControlComponentType.Pump, "dhw", "dhwPump"),
  },
  controllerState: {
    controller: getField(ControllerStateComponentType.PIDController, "dhw", "dhwPumpFlowController"),
  },
  parameters: {
    flow: getField(ParametersType.Flow, "dhw", "heatpumpFlowSetpoint"),
  },
  source: getField(SensorComponentType.Flow, "dhw", "dhwFlowBoosting"),
  sensors: {
    temperature: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureBoostingReturn"),
  },
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Flow sensor",
      componentType: "Flow sensor",
    });
  },
});
