import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { fwdRecoveryTemperatureController } from "../controllers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.TemperatureSensor>({
  controls: {
    pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump2"),
  },
  controllerState: {
    controller: fwdRecoveryTemperatureController,
  },
  custom: {},
  parameters: {
    temperature: getField(ParametersType.Temperature, "thrusters", "coolingTemperature"),
  },
  source: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureFwd"),
  sensors: {
    measurement: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureFwd"),
  },
  get tooltip() {
    return tooltip(this.source);
  },
});
