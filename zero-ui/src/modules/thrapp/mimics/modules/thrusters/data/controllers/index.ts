import { getField } from "@/modules/thrapp/mimics/providers";
import { PIDController } from "@/modules/thrapp/types/fields";
import {
  ControllerStateComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrs/types";

export const heatDumpController: PIDController<SensorComponentType.Temperature> = {
  type: SensorComponentType.Temperature,
  controller: getField(
    ControllerStateComponentType.PIDController,
    "thrusters",
    "heatDumpController",
  ),
};
export const warmupMixController: PIDController<SensorComponentType.Temperature> = {
  type: SensorComponentType.Temperature,
  controller: getField(
    ControllerStateComponentType.PIDController,
    "thrusters",
    "warmupMixController",
  ),
  setpoint: getField(ParametersType.Temperature, "thrusters", "warmupTemperature"),
};

export const aftRecoveryTemperatureController: PIDController<SensorComponentType.Temperature> = {
  type: SensorComponentType.Temperature,
  controller: getField(
    ControllerStateComponentType.PIDController,
    "thrusters",
    "aftRecoveryTemperatureController",
  ),
  setpoint: getField(ParametersType.Temperature, "thrusters", "recoveryTemperature"),
};

export const fwdRecoveryTemperatureController: PIDController<SensorComponentType.Temperature> = {
  type: SensorComponentType.Temperature,
  controller: getField(
    ControllerStateComponentType.PIDController,
    "thrusters",
    "fwdRecoveryTemperatureController",
  ),
  setpoint: getField(ParametersType.Temperature, "thrusters", "recoveryTemperature"),
};

export const pumpController: PIDController<SensorComponentType.Flow> = {
  type: SensorComponentType.Flow,
  controller: getField(ControllerStateComponentType.PIDController, "thrusters", "pumpController"),
};

export const aftFlowController: PIDController<SensorComponentType.Flow> = {
  type: SensorComponentType.Flow,
  controller: getField(
    ControllerStateComponentType.PIDController,
    "thrusters",
    "aftFlowController",
  ),
};

export const fwdFlowController: PIDController<SensorComponentType.Flow> = {
  type: SensorComponentType.Flow,
  controller: getField(
    ControllerStateComponentType.PIDController,
    "thrusters",
    "fwdFlowController",
  ),
};
