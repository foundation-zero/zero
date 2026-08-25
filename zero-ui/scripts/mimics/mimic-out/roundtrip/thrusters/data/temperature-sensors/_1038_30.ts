import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
export default toInstance<MimicComponentType.TemperatureSensor>({
  custom: {},
  controls: {
    pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump1"),
  },
  controllerState: {},
  parameters: {
    temperature: getField(ParametersType.Temperature, "thrusters", "recoveryTemperature"),
  },
  source: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureRecoveryMix"),
  sensors: {
    measurement: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureRecoveryMix"),
  },
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Temperature sensor",
      componentType: "Temperature sensor",
    });
  },
});
