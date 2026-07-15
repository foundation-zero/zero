import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { getField } from "@/modules/thrapp/mimics/providers";
import { MimicComponentType } from "@/modules/thrapp/types";
import {
  ControlFieldDefinitions,
  ControllerStateFieldDefinitions,
  ExtractModuleFields,
  ParameterFieldDefinitions,
} from "@/modules/thrapp/types/fields";
import {
  ControlComponentType,
  ControllerStateComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrs/types";

export const tooltip = (content: Partial<TooltipContent>): TooltipContent => ({
  title: "Pressure sensor",
  itemName: "Pressure sensor",
  ...content,
});

export const controller = getField(
  ControllerStateComponentType.PIDController,
  "dhw",
  "dhwPumpFlowController",
);

export const pump = getField(ControlComponentType.Pump, "dhw", "dhwPump");

export const setpoint = getField(ParametersType.Flow, "dhw", "heatpumpFlowSetpoint");

export const flow = getField(SensorComponentType.Flow, "dhw", "dhwFlowBoosting");

export type PressureSensorControls = ExtractModuleFields<
  ControlFieldDefinitions[MimicComponentType.PressureSensor]
>;

export type PressureSensorParameters = ExtractModuleFields<
  ParameterFieldDefinitions[MimicComponentType.PressureSensor]
>;
export type PressureSensorControllerState = ExtractModuleFields<
  ControllerStateFieldDefinitions[MimicComponentType.PressureSensor]
>;

export const controls: PressureSensorControls = {
  pump,
};
export const controllerState: PressureSensorControllerState = {
  controller,
};
export const parameters: PressureSensorParameters = {
  flow: setpoint,
};
