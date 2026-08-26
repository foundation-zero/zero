import { getField } from "@/modules/thrapp/mimics/providers";
import { PIDController } from "@/modules/thrapp/types/fields";
import {
  ControllerStateComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrsim/types";

export const heatDumpController: PIDController<SensorComponentType.Temperature> = {
  type: SensorComponentType.Temperature,
  controller: getField(
    ControllerStateComponentType.PIDController,
    "thrusters",
    "thrustersHeatDumpController",
  ),
};
export const warmupMixController: PIDController<SensorComponentType.Temperature> = {
  type: SensorComponentType.Temperature,
  controller: getField(
    ControllerStateComponentType.PIDController,
    "thrusters",
    "thrustersWarmupMixController",
  ),
  setpoint: getField(ParametersType.Temperature, "thrusters", "warmupTemperature"),
};

export const aftRecoveryTemperatureController: PIDController<SensorComponentType.Temperature> = {
  type: SensorComponentType.Temperature,
  controller: getField(
    ControllerStateComponentType.PIDController,
    "thrusters",
    "thrustersAftRecoveryTemperatureController",
  ),
  setpoint: getField(ParametersType.Temperature, "thrusters", "recoveryTemperature"),
};

export const fwdRecoveryTemperatureController: PIDController<SensorComponentType.Temperature> = {
  type: SensorComponentType.Temperature,
  controller: getField(
    ControllerStateComponentType.PIDController,
    "thrusters",
    "thrustersFwdRecoveryTemperatureController",
  ),
  setpoint: getField(ParametersType.Temperature, "thrusters", "recoveryTemperature"),
};

export const pumpController: PIDController<SensorComponentType.Flow> = {
  type: SensorComponentType.Flow,
  controller: getField(
    ControllerStateComponentType.PIDController,
    "thrusters",
    "thrustersPumpController",
  ),
};

export const aftFlowController: PIDController<SensorComponentType.Flow> = {
  type: SensorComponentType.Flow,
  controller: getField(
    ControllerStateComponentType.PIDController,
    "thrusters",
    "thrustersAftFlowController",
  ),
};

export const fwdFlowController: PIDController<SensorComponentType.Flow> = {
  type: SensorComponentType.Flow,
  controller: getField(
    ControllerStateComponentType.PIDController,
    "thrusters",
    "thrustersFwdFlowController",
  ),
};
