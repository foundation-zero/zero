import { getField } from "@/modules/thrapp/mimics/providers";
import { PIDController } from "@/modules/thrapp/types/fields";
import {
  ControllerStateComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrsim/types";

export const dcFlowController: PIDController<SensorComponentType.Temperature> = {
  type: SensorComponentType.Temperature,
  controller: getField(ControllerStateComponentType.PIDController, "dhw", "dhwDcFlowController"),
  setpoint: getField(ParametersType.Temperature, "dhw", "fillingTemperatureSetpoint"),
  outputMinimum: getField(ParametersType.FlowControl, "dhw", "dcFlowcontrolMinimumSetpoint"),
};

export const drivesFlowController: PIDController<SensorComponentType.Temperature> = {
  type: SensorComponentType.Temperature,
  controller: getField(
    ControllerStateComponentType.PIDController,
    "dhw",
    "dhwDrivesFlowController",
  ),
  setpoint: getField(ParametersType.Temperature, "dhw", "fillingTemperatureSetpoint"),
  outputMinimum: getField(ParametersType.FlowControl, "dhw", "drivesFlowcontrolMinimumSetpoint"),
};

export const pumpFlowController: PIDController<SensorComponentType.Flow> = {
  type: SensorComponentType.Flow,
  controller: getField(ControllerStateComponentType.PIDController, "dhw", "dhwPumpFlowController"),
  setpoint: getField(ParametersType.Flow, "dhw", "heatpumpFlowSetpoint"),
};

export const pumpTemperatureController: PIDController<SensorComponentType.Flow> = {
  type: SensorComponentType.Flow,
  controller: getField(
    ControllerStateComponentType.PIDController,
    "dhw",
    "dhwPumpTemperatureController",
  ),
  setpoint: getField(ParametersType.Flow, "dhw", "heatpumpFlowSetpoint"),
};
