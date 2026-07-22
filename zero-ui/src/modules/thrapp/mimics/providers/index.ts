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

export const getCustomField = <Module extends keyof ThrsDefinitions>(
  module: Module,
  field: string,
): ModuleField<"custom", Module> => ["custom", module, field];

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
    | undefined
    | "custom" =
    | ControlComponentType
    | SensorComponentType
    | ParametersType
    | ControllerStateComponentType
    | undefined
    | "custom",
  Module extends keyof ThrsDefinitions = keyof ThrsDefinitions,
> = [type: Type, module: Module, field: string];

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

export const DEFAULT_SENSOR_FIELD_VALUE_FIELD: {
  [Type in SensorComponentType]: keyof SensorDefinitionMap[Type];
} = {
  [SensorComponentType.Temperature]: "temperature",
  [SensorComponentType.Pressure]: "pressure",
  [SensorComponentType.Flow]: "flow",
  [SensorComponentType.Pump]: "flow",
  [SensorComponentType.Valve]: "positionRel",
  [SensorComponentType.Thruster]: "active",
  [SensorComponentType.Pcs]: "mode",
  [SensorComponentType.Pcm]: "charged",
  [SensorComponentType.Level]: "level",
  [SensorComponentType.DeltaT]: "deltaT",
  [SensorComponentType.HeatExchanger]: "deltaT",
  [SensorComponentType.CalculatedFlow]: "flow",
  [SensorComponentType.AdsorptionChiller]: "operating",
};

export const DEFAULT_CONTROL_FIELD_VALUE_FIELD: {
  [Type in ControlComponentType]: keyof ControlDefinitionMap[Type];
} = {
  [ControlComponentType.Pump]: "dutypoint",
  [ControlComponentType.Valve]: "setpoint",
  [ControlComponentType.Pcm]: "on",
  [ControlComponentType.Heatpump]: "on",
  [ControlComponentType.AdsorptionChiller]: "enable",
};

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

export const getDefinition = (field: ModuleField) => {
  if (isSensorField(field)) {
    return getSensorDefinition(field[1], field[2]);
  } else if (isControlField(field)) {
    return getControlDefinition(field[1], field[2]);
  } else if (isParameterField(field)) {
    return getParameterDefinition(field[1], field[2]);
  } else if (isControllerStateField(field)) {
    return getControllerStateDefinition(field[1], field[2]);
  } else if (isCustomField(field)) {
    return undefined;
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
