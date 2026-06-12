import { DEFINITIONS, ThrsDefinitions } from "@/modules/thrs/lib/consts";
import {
  ControlComponentType,
  ControlDefinitionMap,
  ControlDefinitions,
  ParameterDefinitionMap,
  ParameterDefinitions,
  ParametersType,
  PickKeys,
  SchemaDefinition,
  SensorComponentType,
  SensorDefinitionMap,
  SensorDefinitions,
} from "@/modules/thrs/types";
import { createContext } from "reka-ui";
import { inject, MaybeRef, provide, ref, Ref } from "vue";
import { MimicComponentState } from "../components/index.ts";

export { default as ControlValue } from "./ControlValue.vue";
export { default as GraphQLProvider } from "./GraphQLProvider.vue";
export { default as MockProvider } from "./MockProvider.vue";
export { default as ParameterValue } from "./ParameterValue.vue";
export { default as SensorValue } from "./SensorValue.vue";

export const getField = <
  Type extends SensorComponentType | ControlComponentType | ParametersType,
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
): ModuleField<Type, Module> => [type, module, field] as ModuleField<Type, Module>;

export type ModuleField<
  Type extends ControlComponentType | SensorComponentType | ParametersType,
  Module extends keyof ThrsDefinitions = keyof ThrsDefinitions,
> = [type: Type, module: Module, field: string];

export interface MimicDataProvider {
  getSensorValue: <Type extends SensorComponentType, Module extends keyof ThrsDefinitions>(
    prop: ModuleField<Type, Module>,
  ) => Ref<SensorDefinitionMap[Type] | undefined>;
  getControlValue: <Type extends ControlComponentType, Module extends keyof ThrsDefinitions>(
    prop: ModuleField<Type, Module>,
  ) => Ref<ControlDefinitionMap[Type] | undefined>;
  getParameterValue: <Type extends ParametersType, Module extends keyof ThrsDefinitions>(
    prop: ModuleField<Type, Module>,
  ) => Ref<ParameterDefinitionMap[Type] | undefined>;
  getComponentState: (
    state?: MaybeRef<MimicComponentState | undefined>,
  ) => Ref<MimicComponentState>;
}

export interface FieldValueProvider<T> {
  value: Ref<T | undefined>;
}

export const [getMimicDataProvider, createMimicDataProvider] =
  createContext<MimicDataProvider>("MimicProvider");

export const provideFieldValue = <T>(value: Ref<T>) => provide("FieldValue", value);
export const provideFieldValueSource = <
  T extends SensorComponentType | ControlComponentType | ParametersType,
>(
  value: ModuleField<T>,
) => provide("FieldValueSource", value);
export const injectFieldValueSource = <
  T extends SensorComponentType | ControlComponentType | ParametersType,
>(
  fallback: ModuleField<T> | undefined = undefined,
) => inject<ModuleField<T> | undefined>("FieldValueSource", fallback);

export const getFieldValue = <T>(
  fallback: Ref<T | undefined> = ref(undefined),
): Ref<T | undefined> => inject<Ref<T | undefined>>("FieldValue", fallback);

export const getSensorDefinition = <K extends keyof ThrsDefinitions>(module: K, field: string) => {
  const definitions: SensorDefinitions = DEFINITIONS[module].sensorValues;
  const definition = definitions[field];

  if (!definition) {
    throw new Error(`No sensor definition found for field: ${field as string}`);
  }

  return definition;
};

export const getControlDefinition = <K extends keyof ThrsDefinitions>(module: K, field: string) => {
  const definitions: ControlDefinitions = DEFINITIONS[module].controlValues;
  const definition = definitions[field];

  if (!definition) {
    throw new Error(`No control definition found for field: ${field as string}`);
  }

  return definition;
};

export const getParameterDefinition = <K extends keyof ThrsDefinitions>(
  module: K,
  field: string,
) => {
  const definitions: ParameterDefinitions = DEFINITIONS[module].parameters;
  const definition = definitions[field];

  if (!definition) {
    throw new Error(`No parameter definition found for field: ${field as string}`);
  }

  return definition;
};
