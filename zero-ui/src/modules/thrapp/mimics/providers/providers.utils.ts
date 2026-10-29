import { DEFINITIONS, ThrsDefinitions } from "@/modules/thrapp/lib/consts";
import {
  ControlComponentType,
  ControlDefinitions,
  ControllerStateComponentType,
  ControllerStateDefinitions,
  ParameterDefinitions,
  ParametersType,
  PickKeys,
  SchemaDefinition,
  SensorComponentType,
  SensorDefinitions,
} from "@/modules/thrapp/types/thrs";
import { createContext } from "reka-ui";
import { inject, provide, ref, Ref } from "vue";
import {
  MimicDataProvider,
  ModuleField,
  Placeholder,
  SchemaDirectiveData,
} from "./providers.types";

export const getCustomField = <Module extends keyof ThrsDefinitions>(
  module: Module,
  data: SchemaDirectiveData,
): ModuleField<"custom", Module> => ["custom", module, data.technicalName ?? "unknown", data];

export const getField = <
  Type extends
    SensorComponentType | ControlComponentType | ParametersType | ControllerStateComponentType,
  Section extends "sensorValues" | "controlValues" | "parameters" | "controllerState" =
    Type extends SensorComponentType
      ? "sensorValues"
      : Type extends ControlComponentType
        ? "controlValues"
        : Type extends ControllerStateComponentType
          ? "controllerState"
          : "parameters",
  Module extends keyof ThrsDefinitions = keyof {
    [
      M in keyof ThrsDefinitions as PickKeys<
        ThrsDefinitions[M][Section],
        SchemaDefinition<Type>
      > extends never
        ? never
        : M
    ]: ThrsDefinitions[M];
  },
>(
  type: Type,
  module: Module,
  field: PickKeys<ThrsDefinitions[Module][Section], SchemaDefinition<Type>> | Placeholder,
): ModuleField<Type, Module> => [type, module, field, null] as ModuleField<Type, Module>;

export const isField = <
  Type extends
    | ControlComponentType
    | SensorComponentType
    | ParametersType
    | ControllerStateComponentType
    | "custom",
>(
  field?: ModuleField<Type | undefined>,
  type?: Type,
): field is ModuleField<Type> => {
  return field?.[0] !== undefined && (type === undefined || field[0] === type);
};

export const isCustomField = <Type extends "custom" = "custom">(
  field?: ModuleField,
): field is ModuleField<Type> => {
  return isField(field, "custom");
};

export const isPlaceholderField = <
  Type extends
    | ControlComponentType
    | SensorComponentType
    | ParametersType
    | ControllerStateComponentType
    | "custom",
>(
  field?: ModuleField<Type | undefined>,
) => {
  return isField(field) && field[2] === "placeholder";
};

export const isSensorField = <Type extends SensorComponentType = SensorComponentType>(
  field?: ModuleField,
  type?: Type,
): field is ModuleField<Type> => {
  return isField(field, type) && field[0].startsWith("sensor:");
};

export const isControlField = <Type extends ControlComponentType = ControlComponentType>(
  field?: ModuleField,
  type?: Type,
): field is ModuleField<Type> => {
  return isField(field, type) && field[0].startsWith("control:");
};

export const isParameterField = <Type extends ParametersType = ParametersType>(
  field?: ModuleField,
  type?: Type,
): field is ModuleField<Type> => {
  return isField(field, type) && field[0].startsWith("parameter:");
};

export const isControllerStateField = <
  Type extends ControllerStateComponentType = ControllerStateComponentType,
>(
  field?: ModuleField,
  type?: Type,
): field is ModuleField<Type> => {
  return isField(field, type) && field[0].startsWith("controller:");
};

export const [getMimicDataProvider, createMimicDataProvider] =
  createContext<MimicDataProvider>("MimicProvider");

export const provideFieldValue = <T>(value: Ref<T>) => provide("FieldValue", value);
export const provideFieldValueData = <T>(value: Ref<T>) => provide("FieldValueData", value);
export const provideFieldValueField = (field?: string) => provide("FieldValueField", field);
export const injectFieldValueField = <T extends string = string>() =>
  inject<T | undefined>("FieldValueField");

export const provideFieldValueSource = <
  T extends
    SensorComponentType | ControlComponentType | ParametersType | ControllerStateComponentType,
>(
  value: ModuleField<T>,
) => provide("FieldValueSource", value);

export const injectFieldValueSource = <
  T extends
    SensorComponentType | ControlComponentType | ParametersType | ControllerStateComponentType,
>(
  fallback: ModuleField<T> | undefined = undefined,
) => inject<ModuleField<T> | undefined>("FieldValueSource", fallback);

export const getFieldValue = <T>(
  fallback: Ref<T | undefined> = ref(undefined),
): Ref<T | undefined> => inject<Ref<T | undefined>>("FieldValue", fallback);
export const getFieldValueData = <T>(
  fallback: Ref<T | undefined> = ref(undefined),
): Ref<T | undefined> => inject<Ref<T | undefined>>("FieldValueData", fallback);

export const getDefinition = (field: ModuleField) => {
  const [_, module, fieldName, customData] = field;

  if (fieldName === "placeholder") {
    return undefined;
  }
  if (isSensorField(field)) {
    return getSensorDefinition(module, fieldName);
  } else if (isControlField(field)) {
    return getControlDefinition(module, fieldName);
  } else if (isParameterField(field)) {
    return getParameterDefinition(module, fieldName);
  } else if (isControllerStateField(field)) {
    return getControllerStateDefinition(module, fieldName);
  } else if (isCustomField(field)) {
    return customData;
  }
};

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

export const serializeField = (field: ModuleField | undefined): string | undefined =>
  field?.slice(0, 3).join(".");

export const deserializeField = (string: string): ModuleField | undefined => {
  const parts = string.split(".");
  if (parts.length !== 3) return;

  return parts as ModuleField;
};
