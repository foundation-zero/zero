import { TooltipContent } from "@/modules/thrapp/components/tooltip";

import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";

import {
  ControlFieldDefinitions,
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
  ControlComponentType.PIDController,
  "boilers",
  "boilersPumpTemperatureController",
);

export const actuator = getField(ControlComponentType.Pump, "boilers", "boilersPump");

export const setpoint = getField(
  ParametersType.Temperature,
  "boilers",
  "heatpumpTemperatureSetpoint",
);

export type TemperatureSensorControls = ExtractModuleFields<
  ControlFieldDefinitions[MimicComponentType.TemperatureSensor]
>;

export type TemperatureSensorParameters = ExtractModuleFields<
  ParameterFieldDefinitions[MimicComponentType.TemperatureSensor]
>;

export const controls: TemperatureSensorControls = {
  controller,
  pump: actuator,
};

export const parameters: TemperatureSensorParameters = {
  temperature: setpoint,
};

export const measurement = getField(
  SensorComponentType.Temperature,
  "boilers",
  "boilersTemperatureBoostingSupply",
);
