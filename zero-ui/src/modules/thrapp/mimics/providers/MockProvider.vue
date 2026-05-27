<script setup lang="ts" generic="K extends keyof ThrsModules">
import { ThrsDefinitions, ThrsModules } from "@/modules/thrs/lib/consts.types";
import {
  ControlComponentType,
  ControlDefinitionMap,
  SensorComponentType,
  SensorDefinitionMap,
} from "@/modules/thrs/types";
import { Ref } from "vue";
import { createMimicDataProvider, getControlDefinition, getSensorDefinition } from ".";
import { ModuleProp } from "../instances";
import { CONTROL_VALUES_FACTORY, SENSOR_VALUES_FACTORY } from "./mock-helpers";

const getSensorValue = <Type extends SensorComponentType, Module extends keyof ThrsDefinitions>([
  _type,
  module,
  field,
]: ModuleProp<Type, Module>): Ref<SensorDefinitionMap[Type] | undefined> => {
  const { componentType } = getSensorDefinition(module, field);
  return SENSOR_VALUES_FACTORY[componentType]() as Ref<SensorDefinitionMap[Type] | undefined>;
};

const getControlValue = <Type extends ControlComponentType, Module extends keyof ThrsDefinitions>([
  _type,
  module,
  field,
]: ModuleProp<Type, Module>): Ref<ControlDefinitionMap[Type] | undefined> => {
  const { componentType } = getControlDefinition(module, field);
  return CONTROL_VALUES_FACTORY[componentType]() as Ref<ControlDefinitionMap[Type] | undefined>;
};

createMimicDataProvider({
  getSensorValue,
  getControlValue,
});
</script>

<template>
  <slot />
</template>
