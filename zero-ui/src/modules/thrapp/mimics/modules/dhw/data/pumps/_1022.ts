import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { pumpFlowController, pumpTemperatureController } from "../controllers";
import { fieldTooltip } from "../shared";

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
  sensors: {
    pressure: getField(SensorComponentType.Pressure, "dhw", "dhwPressure"),
  },
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Pump",
      itemName: "Circulation pump hot freshwater",
    });
  },
});
