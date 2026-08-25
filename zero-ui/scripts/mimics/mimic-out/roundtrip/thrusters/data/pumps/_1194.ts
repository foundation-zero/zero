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
  controls: {
    pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump1"),
  },
  controllerState: {},
  parameters: {
    flow: getField(ParametersType.Flow, "thrusters", "thrustersMinimumFlow"),
    temperature: getField(ParametersType.Temperature, "thrusters", "recoveryTemperature"),
  },
  source: getField(SensorComponentType.Pump, "thrusters", "thrustersPump1"),
  sensors: {},
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Pump",
      componentType: "Thrusters circulation pump AFT",
    });
  },
});
