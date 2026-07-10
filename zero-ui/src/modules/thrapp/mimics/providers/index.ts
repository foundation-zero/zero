import { DEFINITIONS, ThrsDefinitions } from "@/modules/thrs/lib/consts";
import {
  ControlComponentType,
  ControlDefinitionMap,
  ControlDefinitions,
  ControllerStateComponentType,
  ControllerStateDefinitionMap,
  ControllerStateDefinitions,
  ControlValues,
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

export { default as ControllerStateValue } from "./ControllerStateValue.vue";
export { default as ControlValue } from "./ControlValue.vue";
export { default as ControlValueForm } from "./ControlValueForm.vue";
export { default as GraphQLProvider } from "./GraphQLProvider.vue";
export { default as MockProvider } from "./MockProvider.vue";
export { default as ParameterValue } from "./ParameterValue.vue";
export { default as ParameterValueForm } from "./ParameterValueForm.vue";
export { default as SensorValue } from "./SensorValue.vue";

export const getField = <
  Type extends
    | SensorComponentType
    | ControlComponentType
    | ParametersType
    | ControllerStateComponentType,
  Section extends "sensorValues" | "controlValues" | "parameters" | "controllerState" =
    Type extends SensorComponentType
      ? "sensorValues"
      : Type extends ControlComponentType
        ? "controlValues"
        : Type extends ControllerStateComponentType
          ? "controllerState"
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
  Type extends
    | ControlComponentType
    | SensorComponentType
    | ParametersType
    | ControllerStateComponentType
    | undefined,
  Module extends keyof ThrsDefinitions = keyof ThrsDefinitions,
> = [type: Type, module: Module, field: string];

export interface MimicDataProvider {
  getSensorValue: <Type extends SensorComponentType, Module extends keyof ThrsDefinitions>(
    prop: ModuleField<Type, Module>,
  ) => Ref<SensorDefinitionMap[Type] | undefined>;
  getControlValue: <Type extends ControlComponentType, Module extends keyof ThrsDefinitions>(
    prop: ModuleField<Type, Module>,
  ) => Ref<ControlDefinitionMap[Type] | undefined>;
  getParameter: <Type extends ParametersType, Module extends keyof ThrsDefinitions>(
    prop: ModuleField<Type, Module>,
  ) => Ref<ParameterDefinitionMap[Type] | undefined>;
  getComponentState: (
    state?: MaybeRef<MimicComponentState | undefined>,
  ) => Ref<MimicComponentState>;
  getControllerState: <
    Type extends ControllerStateComponentType,
    Module extends keyof ThrsDefinitions,
  >(
    prop: ModuleField<Type, Module>,
  ) => Ref<ControllerStateDefinitionMap[Type] | undefined>;
  setControlValue: <Type extends ControlComponentType, Module extends keyof ThrsDefinitions>(
    prop: ModuleField<Type, Module>,
    value: ControlValues<Type>,
  ) => Promise<void>;
  setParameter: <Type extends ParametersType, Module extends keyof ThrsDefinitions>(
    prop: ModuleField<Type, Module>,
    value: ParameterDefinitionMap[Type],
  ) => Promise<void>;
  // setControllerState: <
  //   Type extends ControllerStateComponentType,
  //   Module extends keyof ThrsDefinitions,
  // >(
  //   prop: ModuleField<Type, Module>,
  //   value: ControllerStateDefinitionMap[Type],
  // ) => Promise<void>;
}

export interface FieldValueProvider<T> {
  value: Ref<T | undefined>;
}

export const [getMimicDataProvider, createMimicDataProvider] =
  createContext<MimicDataProvider>("MimicProvider");

export const provideFieldValue = <T>(value: Ref<T>) => provide("FieldValue", value);
export const provideFieldValueField = (field?: string) => provide("FieldValueField", field);
export const injectFieldValueField = <T extends string = string>() =>
  inject<T | undefined>("FieldValueField");

export const provideFieldValueSource = <
  T extends
    | SensorComponentType
    | ControlComponentType
    | ParametersType
    | ControllerStateComponentType,
>(
  value: ModuleField<T>,
) => provide("FieldValueSource", value);

export const injectFieldValueSource = <
  T extends
    | SensorComponentType
    | ControlComponentType
    | ParametersType
    | ControllerStateComponentType,
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
    console.error(`No sensor definition found for field: ${field as string}`);
  }

  return definition;
};

export const getControlDefinition = <K extends keyof ThrsDefinitions>(module: K, field: string) => {
  const definitions: ControlDefinitions = DEFINITIONS[module].controlValues;
  const definition = definitions[field];

  if (!definition) {
    console.error(`No control definition found for field: ${field as string}`);
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
    console.error(`No parameter definition found for field: ${field as string}`);
  }

  return definition;
};

export const getControllerStateDefinition = <K extends keyof ThrsDefinitions>(
  module: K,
  field: string,
) => {
  const definitions: ControllerStateDefinitions = DEFINITIONS[module].controllerState;
  const definition = definitions[field];

  if (!definition) {
    console.error(`No control definition found for field: ${field as string}`);
  }

  return definition;
};
