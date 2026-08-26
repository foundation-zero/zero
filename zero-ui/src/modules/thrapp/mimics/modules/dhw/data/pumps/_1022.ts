import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
import { pumpFlowController, pumpTemperatureController } from "../controllers";

export default toInstance<MimicComponentType.Pump>({
  custom: {
    temperatureController: pumpTemperatureController,
    flowController: pumpFlowController,
  },
  controllerState: {},
  source: getField(SensorComponentType.Pump, "dhw", "dhwPump"),
  controls: {
    pump: getField(ControlComponentType.Pump, "dhw", "dhwPump"),
  },
  parameters: {
    flow: getField(ParametersType.Flow, "dhw", "heatpumpFlowSetpoint"),
    temperature: getField(ParametersType.Temperature, "dhw", "heatpumpTemperatureSetpoint"),
  },
  sensors: {},
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Pump",
      componentType: "Circulation pump boosting",
    });
  },
});
