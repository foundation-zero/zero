import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { getField } from "../../../providers";
import { toTemperatureSensor } from "../../helpers";

export default toTemperatureSensor({
  controls: {
    pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump1"),
  },
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
});
