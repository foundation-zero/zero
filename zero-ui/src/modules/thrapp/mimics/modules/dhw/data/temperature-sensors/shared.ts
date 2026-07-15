import { TooltipContent } from "@/modules/thrapp/components/tooltip";

import {
  ControlComponentType,
  ControllerStateComponentType,
  ParametersType,
} from "@/modules/thrs/types";

import {
  ControlFieldDefinitions,
  ControllerStateFieldDefinitions,
  ExtractModuleFields,
  ParameterFieldDefinitions,
} from "@/modules/thrapp/types/fields";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";

export const tooltip = (content: Partial<TooltipContent>): TooltipContent => ({
  title: "Temperature sensor",
  itemName: "Temperature sensor",
  ...content,
});

export const controller = getField(
  ControllerStateComponentType.PIDController,
  "dhw",
  "dhwPumpTemperatureController",
);

export const actuator = getField(ControlComponentType.Pump, "dhw", "dhwPump");

export const setpoint = getField(ParametersType.Temperature, "dhw", "heatpumpTemperatureSetpoint");

export type TemperatureSensorControls = ExtractModuleFields<
  ControlFieldDefinitions[MimicComponentType.TemperatureSensor]
>;

export type TemperatureSensorParameters = ExtractModuleFields<
  ParameterFieldDefinitions[MimicComponentType.TemperatureSensor]
>;

export type TemperatureSensorControllerState = ExtractModuleFields<
  ControllerStateFieldDefinitions[MimicComponentType.TemperatureSensor]
>;

export const controllerState: TemperatureSensorControllerState = {
  controller,
};

export const parameters: TemperatureSensorParameters = {
  temperature: setpoint,
};
