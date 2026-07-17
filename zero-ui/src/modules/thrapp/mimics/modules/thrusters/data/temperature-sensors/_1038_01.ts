import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { thrustersPidController } from "../helpers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.TemperatureSensor>({
  controls: {
    pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump1"),
  },
  controllerState: {
    controller: thrustersPidController("aftTemperatureController"),
  },
  custom: {},
  parameters: {
    temperature: getField(ParametersType.Temperature, "thrusters", "warmupTemperature"),
  },
  source: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureAft"),
  sensors: {
    measurement: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureAft"),
  },
  tooltip: tooltip("1038-01", "thrusters-temperature-aft"),
});
