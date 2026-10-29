import { ThrsDefinitions } from "@/modules/thrapp/lib/consts";
import {
  ControlComponentType,
  ControlDefinitionMap,
  ControllerStateComponentType,
  ControllerStateDefinitionMap,
  ControlValues,
  ParameterDefinitionMap,
  ParametersType,
  SensorComponentType,
  SensorDefinitionMap,
} from "@/modules/thrapp/types/thrs";
import { MaybeRef, Ref } from "vue";
import { MimicComponentState } from "../components";

export type SchemaDirectiveData = {
  title?: string;
  yardTag?: string;
  technicalName?: string;
};

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
  CustomData extends SchemaDirectiveData | null = Type extends "custom"
    ? SchemaDirectiveData
    : null,
> = [type: Type, module: Module, field: string, customData: CustomData];

export type Placeholder = "placeholder";

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
