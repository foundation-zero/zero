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
    temperature: getField(ParametersType.Temperature, "thrusters", "warmupTemperature"),
  },
  source: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureAft"),
  sensors: {
    measurement: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureAft"),
  },
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Temperature sensor",
      componentType: "Temperature sensor",
    });
  },
});
