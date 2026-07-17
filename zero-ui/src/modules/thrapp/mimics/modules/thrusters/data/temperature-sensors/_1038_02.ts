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
    controller: thrustersPidController("fwdTemperatureController"),
  },
  custom: {},
  parameters: {
    temperature: getField(ParametersType.Temperature, "thrusters", "coolingTemperature"),
  },
  source: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureFwd"),
  sensors: {
    measurement: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureFwd"),
  },
  tooltip: tooltip("1038-02", "thrusters-temperature-fwd"),
});
