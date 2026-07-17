import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { thrustersPidController } from "../helpers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.Pump>({
  custom: {},
  source: getField(SensorComponentType.Pump, "thrusters", "thrustersPump2"),
  controllerState: {
    flowController: thrustersPidController("pump2FlowController"),
    temperatureController: thrustersPidController("pump2TemperatureController"),
  },
  controls: {
    pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump2"),
  },
  parameters: {
    flow: getField(ParametersType.Flow, "thrusters", "thrustersMaximumFlow"),
    temperature: getField(ParametersType.Temperature, "thrusters", "maximumSupplyTemperature"),
  },
  sensors: {
    pressure: getField(SensorComponentType.Pressure, "thrusters", "thrustersPressureSystem"),
    flowMeasurement: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowFwd"),
    temperatureMeasurement: getField(
      SensorComponentType.Temperature,
      "thrusters",
      "thrustersTemperatureFwd",
    ),
  },
  tooltip: tooltip("1195", "thrusters-pump-2", "Thrusters circulation pump FWD"),
});
