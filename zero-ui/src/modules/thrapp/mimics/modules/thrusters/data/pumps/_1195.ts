import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
import { pumpController } from "../controllers";

export default toInstance<MimicComponentType.Pump>({
  custom: {
    flowController: pumpController,
  },
  source: getField(SensorComponentType.Pump, "thrusters", "thrustersPump2"),
  controllerState: {},
  controls: {
    pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump2"),
  },
  parameters: {
    flow: getField(ParametersType.Flow, "thrusters", "thrustersMaximumFlow"),
    temperature: getField(ParametersType.Temperature, "thrusters", "maximumSupplyTemperature"),
  },
  sensors: {},
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Pump",
      componentType: "Thrusters circulation pump FWD",
    });
  },
});
