import { DEFINITIONS, ThrsDefinitions } from "@/modules/thrs/lib/consts";
import {
  ControlComponentType,
  ControlDefinitionMap,
  ControlDefinitions,
  ParameterType,
  PickKeys,
  SchemaDefinition,
  SensorComponentType,
  SensorDefinitionMap,
  SensorDefinitions,
} from "@/modules/thrs/types";
import { createContext } from "reka-ui";
import { Ref } from "vue";

export { default as GraphQLProvider } from "./GraphQLProvider.vue";
export { default as MockProvider } from "./MockProvider.vue";

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
): ModuleField<Type, Module> => [type, module, field] as ModuleField<Type, Module>;

export type ModuleField<
  Type extends ControlComponentType | SensorComponentType | ParameterType,
  Module extends keyof ThrsDefinitions = keyof ThrsDefinitions,
> = [type: Type, module: Module, field: string];

export interface MimicDataProvider {
  getSensorValue: <Type extends SensorComponentType, Module extends keyof ThrsDefinitions>(
    prop: ModuleField<Type, Module>,
  ) => Ref<SensorDefinitionMap[Type] | undefined>;
  getControlValue: <Type extends ControlComponentType, Module extends keyof ThrsDefinitions>(
    prop: ModuleField<Type, Module>,
  ) => Ref<ControlDefinitionMap[Type] | undefined>;
}

export const [getMimicDataProvider, createMimicDataProvider] =
  createContext<MimicDataProvider>("MimicProvider");

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
