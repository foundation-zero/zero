<script setup lang="ts" generic="K extends keyof ThrsModules">
import { ThrsDefinitions, ThrsModules } from "@/modules/thrsim/lib/consts.types";
import {
  ControlComponentType,
  ControlDefinitionMap,
  ControllerStateComponentType,
  ControllerStateDefinitionMap,
  ParameterDefinitionMap,
  ParametersType,
  SensorComponentType,
  SensorDefinitionMap,
} from "@/modules/thrsim/types";
import { Ref } from "vue";
import {
  createMimicDataProvider,
  getControlDefinition,
  getControllerStateDefinition,
  getParameterDefinition,
  getSensorDefinition,
  ModuleField,
} from ".";
import { MimicComponentState } from "../components";
import {
  CONTROL_VALUES_FACTORY,
  CONTROLLER_VALUE_VALUES_FACTORY,
  PARAMETER_VALUES_FACTORY,
  SENSOR_VALUES_FACTORY,
  useRandomizedState,
} from "./mock-helpers";

const getSensorValue = <Type extends SensorComponentType, Module extends keyof ThrsDefinitions>([
  _type,
  module,
  field,
]: ModuleField<Type, Module>): Ref<SensorDefinitionMap[Type] | undefined> => {
  const { componentType } = getSensorDefinition(module, field);
  return SENSOR_VALUES_FACTORY[componentType]() as Ref<SensorDefinitionMap[Type] | undefined>;
};

const getControlValue = <Type extends ControlComponentType, Module extends keyof ThrsDefinitions>([
  _type,
  module,
  field,
]: ModuleField<Type, Module>): Ref<ControlDefinitionMap[Type] | undefined> => {
  const { componentType } = getControlDefinition(module, field);
  return CONTROL_VALUES_FACTORY[componentType]() as Ref<ControlDefinitionMap[Type] | undefined>;
};

const getParameterValue = <Type extends ParametersType, Module extends keyof ThrsDefinitions>([
  _type,
  module,
  field,
]: ModuleField<Type, Module>): Ref<ParameterDefinitionMap[Type] | undefined> => {
  const { componentType } = getParameterDefinition(module, field);
  return PARAMETER_VALUES_FACTORY[componentType]() as Ref<ParameterDefinitionMap[Type] | undefined>;
};

const getControllerState = <
  Type extends ControllerStateComponentType,
  Module extends keyof ThrsDefinitions,
>([_type, module, field]: ModuleField<Type, Module>): Ref<
  ControllerStateDefinitionMap[Type] | undefined
> => {
  const { componentType } = getControllerStateDefinition(module, field);
  return CONTROLLER_VALUE_VALUES_FACTORY[componentType]() as Ref<
    ControllerStateDefinitionMap[Type] | undefined
  >;
};
createMimicDataProvider({
  getSensorValue,
  getControlValue,
  getParameter: getParameterValue,
  getControllerState,
  setParameter: async () => {},
  setControlValue: async () => {},
  getComponentState: () =>
    useRandomizedState([
      MimicComponentState.Normal,
      MimicComponentState.Alarm,
      MimicComponentState.Manual,
    ]),
});
</script>

<template>
  <slot />
</template>
