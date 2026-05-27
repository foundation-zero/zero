import { DEFINITIONS, ThrsDefinitions } from "@/modules/thrs/lib/consts";
import {
  ControlComponentType,
  ControlDefinitionMap,
  ControlDefinitions,
  SensorComponentType,
  SensorDefinitionMap,
  SensorDefinitions,
} from "@/modules/thrs/types";
import { createContext } from "reka-ui";
import { Ref } from "vue";
import { ModuleProp } from "../instances";

export { default as GraphQLProvider } from "./GraphQLProvider.vue";
export { default as MockProvider } from "./MockProvider.vue";

export interface MimicDataProvider {
  getSensorValue: <Type extends SensorComponentType, Module extends keyof ThrsDefinitions>(
    prop: ModuleProp<Type, Module>,
  ) => Ref<SensorDefinitionMap[Type] | undefined>;
  getControlValue: <Type extends ControlComponentType, Module extends keyof ThrsDefinitions>(
    prop: ModuleProp<Type, Module>,
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
