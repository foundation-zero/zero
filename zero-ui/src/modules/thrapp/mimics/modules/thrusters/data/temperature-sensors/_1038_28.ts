import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { thrustersPidController } from "../helpers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.TemperatureSensor>({
  controls: {
    pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump2"),
  },
  controllerState: {
    controller: thrustersPidController("supplyTemperatureController"),
  },
  custom: {},
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
  tooltip: tooltip("1038-28", "thrusters-temperature-supply"),
});
