import { useIntervalFn } from "@vueuse/core";
import { MimicComponentBaseProps } from "../components";

import { refValue } from "@/modules/common/lib/utils";
import { ThrsDefinitions } from "@/modules/thrs/lib/consts";
import {
  ControlComponentType,
  ParameterType,
  PickKeys,
  SchemaDefinition,
  SensorComponentType,
} from "@/modules/thrs/types/index.ts";
import { computed, MaybeRef, ref } from "vue";
export { default as ActuatedValveInstance } from "./ActuatedValveInstance.vue";
export { default as CheckValveInstance } from "./CheckValveInstance.vue";
export { default as FlowSensorInstance } from "./FlowSensorInstance.vue";
export { default as HeatExchangerInstance } from "./HeatExchangerInstance.vue";
export { default as HeatExchangerLabelInstance } from "./HeatExchangerLabelInstance.vue";
export { default as LevelSensorInstance } from "./LevelSensorInstance.vue";
export { default as LoopCircuitInstance } from "./LoopCircuitInstance.vue";
export { default as ManualValveInstance } from "./ManualValveInstance.vue";
export { default as PipeHeatExchangerInstance } from "./PipeHeatExchangerInstance.vue";
export { default as PressureGaugeInstance } from "./PressureGaugeInstance.vue";
export { default as PressureSensorInstance } from "./PressureSensorInstance.vue";
export { default as PumpInstance } from "./PumpInstance.vue";
export { default as TemperatureSensorInstance } from "./TemperatureSensorInstance.vue";

export type YardTags<T extends string> = Record<T, string>;
export type YardTagProps<T extends string> = {
  yardTags: YardTags<T>;
};
export type TitleProps = {
  title: string;
};
export type MimicComponentInstanceProps = MimicComponentBaseProps & {
  x?: number | string;
  y?: number | string;
  tagId?: string;
};

export const getField = <
  Type extends SensorComponentType | ControlComponentType | ParameterType,
  Section extends "sensorValues" | "controlValues" | "parameters" = Type extends SensorComponentType
    ? "sensorValues"
    : Type extends ControlComponentType
      ? "controlValues"
      : "parameters",
  Module extends keyof ThrsDefinitions = keyof {
    [M in keyof ThrsDefinitions as PickKeys<
      ThrsDefinitions[M][Section],
      SchemaDefinition<Type>
    > extends never
      ? never
      : M]: ThrsDefinitions[M];
  },
>(
  type: Type,
  module: Module,
  field: PickKeys<ThrsDefinitions[Module][Section], SchemaDefinition<Type>>,
): ModuleProp<Type, Module> => [type, module, field] as ModuleProp<Type, Module>;

export type ModuleProps<
  Input extends Record<string, ControlComponentType | SensorComponentType | ParameterType>,
> = {
  [K in keyof Input]: ModuleProp<Input[K]>;
};

export type ModuleProp<
  Type extends ControlComponentType | SensorComponentType | ParameterType,
  Module extends keyof ThrsDefinitions = keyof ThrsDefinitions,
> = [type: Type, module: Module, field: string];

export const useRandomizedValue = <T>(valueFn: () => T, interval = 10_000) => {
  const value = ref<T>(valueFn());

  useIntervalFn(() => (value.value = valueFn()), interval);

  return value;
};

export const useRandomizedState = <T>(possibleValues: T[], interval = 10_000) =>
  useRandomizedValue(
    () => possibleValues[Math.floor(Math.random() * possibleValues.length)],
    interval,
  );

export const useDeltaT = (tIn: MaybeRef<number>, tOut: MaybeRef<number>) =>
  computed(() => refValue(tOut) - refValue(tIn));

export const useRandomizedNumber = (min: number, max: number, interval = 10_000) =>
  useRandomizedValue(() => Math.floor(Math.random() * (max - min + 1)) + min, interval);

export const useRandomizedRatio = (interval = 10_000) =>
  useRandomizedValue(() => Math.random(), interval);

export const useRandomizedBoolean = (interval = 10_000) =>
  useRandomizedValue(() => Math.random() < 0.5, interval);
