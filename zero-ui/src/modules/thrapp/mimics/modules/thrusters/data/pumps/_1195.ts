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
  source: getField(SensorComponentType.Pump, "thrusters", "thrustersPump2"),
  controllerState: {},
  controls: {
    pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump2"),
  },
  parameters: {
    flow: getField(ParametersType.Flow, "thrusters", "thrustersMaximumFlow"),
    temperature: getField(ParametersType.Temperature, "thrusters", "maximumSupplyTemperature"),
  },
  sensors: {
    pressure: getField(SensorComponentType.Pressure, "thrusters", "thrustersPressureSystem"),
  },
  tooltip: tooltip("1195", "thrusters-pump-2", "Thrusters circulation pump FWD"),
});
