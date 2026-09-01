import { getField } from "@/modules/thrapp/mimics/providers";
import { PIDController } from "@/modules/thrapp/types/fields";
import {
  ControllerStateComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrsim/types";

export const pvtHeatDumpController: PIDController<SensorComponentType.Temperature> = {
  type: SensorComponentType.Temperature,
  controller: getField(ControllerStateComponentType.PIDController, "pvt", "pvtHeatDumpController"),
  measurement: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureSupply"),
  setpoint: getField(ParametersType.Temperature, "pvt", "maximumSupplyTemperature"),
};

export const pvtMainFwdPumpController: PIDController<SensorComponentType.Temperature> = {
  type: SensorComponentType.Temperature,
  controller: getField(
    ControllerStateComponentType.PIDController,
    "pvt",
    "pvtMainFwdPumpController",
  ),
  measurement: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainFwdReturn"),
  setpoint: getField(ParametersType.Temperature, "pvt", "recoveryTemperature"),
};

export const pvtMainAftPumpController: PIDController<SensorComponentType.Temperature> = {
  type: SensorComponentType.Temperature,
  controller: getField(
    ControllerStateComponentType.PIDController,
    "pvt",
    "pvtMainAftPumpController",
  ),
  measurement: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainAftReturn"),
  setpoint: getField(ParametersType.Temperature, "pvt", "recoveryTemperature"),
};

export const pvtOwnersPumpController: PIDController<SensorComponentType.Temperature> = {
  type: SensorComponentType.Temperature,
  controller: getField(
    ControllerStateComponentType.PIDController,
    "pvt",
    "pvtOwnersPumpController",
  ),
  measurement: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersReturn"),
  setpoint: getField(ParametersType.Temperature, "pvt", "recoveryTemperature"),
};

export const pvtMainFwdWarmupMixController: PIDController<SensorComponentType.Temperature> = {
  type: SensorComponentType.Temperature,
  controller: getField(
    ControllerStateComponentType.PIDController,
    "pvt",
    "pvtMainFwdWarmupMixController",
  ),
  measurement: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainFwdReturn"),
  setpoint: getField(ParametersType.Temperature, "pvt", "warmupTemperature"),
};

export const pvtMainAftWarmupMixController: PIDController<SensorComponentType.Temperature> = {
  type: SensorComponentType.Temperature,
  controller: getField(
    ControllerStateComponentType.PIDController,
    "pvt",
    "pvtMainAftWarmupMixController",
  ),
  measurement: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainAftReturn"),
  setpoint: getField(ParametersType.Temperature, "pvt", "warmupTemperature"),
};

export const pvtOwnersWarmupMixController: PIDController<SensorComponentType.Temperature> = {
  type: SensorComponentType.Temperature,
  controller: getField(
    ControllerStateComponentType.PIDController,
    "pvt",
    "pvtOwnersWarmupMixController",
  ),
  measurement: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersReturn"),
  setpoint: getField(ParametersType.Temperature, "pvt", "warmupTemperature"),
};
