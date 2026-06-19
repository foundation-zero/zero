import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { getField } from "@/modules/thrapp/mimics/providers";
import { MimicComponentType } from "@/modules/thrapp/types";
import {
  ControlFieldDefinitions,
  ExtractModuleFields,
  ParameterFieldDefinitions,
} from "@/modules/thrapp/types/fields";
import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";

export const tooltip = (content: Partial<TooltipContent>): TooltipContent => ({
  title: "Pressure sensor",
  itemName: "Pressure sensor",
  ...content,
});

export const controller = getField(
  ControlComponentType.PIDController,
  "boilers",
  "boilersPumpFlowController",
);

export const pump = getField(ControlComponentType.Pump, "boilers", "boilersPump");

export const setpoint = getField(ParametersType.Flow, "boilers", "heatpumpFlowSetpoint");

export const flow = getField(SensorComponentType.Flow, "boilers", "boilersFlowBoosting");

export type PressureSensorControls = ExtractModuleFields<
  ControlFieldDefinitions[MimicComponentType.PressureSensor]
>;

export type PressureSensorParameters = ExtractModuleFields<
  ParameterFieldDefinitions[MimicComponentType.PressureSensor]
>;

export const controls: PressureSensorControls = {
  controller,
  pump,
};

export const parameters: PressureSensorParameters = {
  flow: setpoint,
};
