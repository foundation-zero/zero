import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { getField } from "../../../providers";
import { toTemperatureSensor } from "../../helpers";

export default toTemperatureSensor({
  controls: {
    pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump1"),
  },
  parameters: {
    temperature: getField(ParametersType.Temperature, "thrusters", "warmupTemperature"),
  },
  source: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureAft"),
  sensors: {
    measurement: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureAft"),
  },
});
