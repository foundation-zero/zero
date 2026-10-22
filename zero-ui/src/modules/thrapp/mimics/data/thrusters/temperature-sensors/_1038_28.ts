import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { getField } from "../../../providers";
import { toTemperatureSensor } from "../../helpers";

export default toTemperatureSensor({
  controls: {
    pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump2"),
  },
  parameters: {
    temperature: getField(ParametersType.Temperature, "thrusters", "maximumSupplyTemperature"),
  },
  source: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureSupply"),
  sensors: {
    measurement: getField(
      SensorComponentType.Temperature,
      "thrusters",
      "thrustersTemperatureSupply",
    ),
  },
});
