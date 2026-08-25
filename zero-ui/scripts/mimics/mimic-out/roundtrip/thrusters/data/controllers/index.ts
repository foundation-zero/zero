import { getField } from "@/modules/thrapp/mimics/providers";
import { PIDController } from "@/modules/thrapp/types/fields";
import {
  ControllerStateComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrsim/types";

export const fwdRecoveryTemperatureController: PIDController<SensorComponentType.Temperature> = {
  type: SensorComponentType.Temperature,
  controller: getField(ControllerStateComponentType.PIDController, "thrusters", "thrustersFwdRecoveryTemperatureController"),
  setpoint: getField(ParametersType.Temperature, "thrusters", "recoveryTemperature"),
};

export const pumpController: PIDController<SensorComponentType.Flow> = {
  type: SensorComponentType.Flow,
  controller: getField(ControllerStateComponentType.PIDController, "thrusters", "thrustersPumpController"),
};
