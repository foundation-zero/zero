import {
  ControlComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrapp/types/thrs";
import { getField } from "../../../providers";
import { toTemperatureSensor } from "../../helpers";
import { fwdRecoveryTemperatureController } from "../controllers";

export default toTemperatureSensor({
  controls: {
    pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump2"),
  },
  controllerState: {
    controller: fwdRecoveryTemperatureController,
  },
  parameters: {
    temperature: getField(ParametersType.Temperature, "thrusters", "coolingTemperature"),
  },
  source: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureFwd"),
  sensors: {
    measurement: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureFwd"),
  },
});
