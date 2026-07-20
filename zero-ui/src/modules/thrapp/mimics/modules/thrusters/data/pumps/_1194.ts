import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { pumpController } from "../controllers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.Pump>({
  custom: {
    flowController: pumpController,
  },
  source: getField(SensorComponentType.Pump, "thrusters", "thrustersPump1"),
  controllerState: {},
  controls: {
    pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump1"),
  },
  parameters: {
    flow: getField(ParametersType.Flow, "thrusters", "thrustersMinimumFlow"),
    temperature: getField(ParametersType.Temperature, "thrusters", "recoveryTemperature"),
  },
  sensors: {
    pressure: getField(SensorComponentType.Pressure, "thrusters", "thrustersPressureDischarge"),
  },
  tooltip: tooltip("1194", "thrusters-pump-1", "Thrusters circulation pump AFT"),
});
