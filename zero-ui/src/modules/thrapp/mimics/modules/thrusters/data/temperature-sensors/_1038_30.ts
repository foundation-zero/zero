import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.TemperatureSensor>({
  controls: {
    pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump1"),
  },
  controllerState: {},
  custom: {},
  parameters: {
    temperature: getField(ParametersType.Temperature, "thrusters", "recoveryTemperature"),
  },
  source: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureRecoveryMix"),
  sensors: {
    measurement: getField(
      SensorComponentType.Temperature,
      "thrusters",
      "thrustersTemperatureRecoveryMix",
    ),
  },
  get tooltip() {
    return tooltip(this.source);
  },
});
