<script setup lang="ts" generic="K extends keyof THRS['modules']">
import { THRS, ThrsDefinitions, ThrsModules } from "@/modules/thrs/lib/consts.types";
import { useThrsHistory } from "@/modules/thrs/stores/history";
import {
  ControlComponentType,
  ControlDefinitionMap,
  SensorComponentType,
  SensorDefinitionMap,
} from "@/modules/thrs/types";
import { computed, Ref, toRefs } from "vue";
import { createMimicDataProvider, ModuleField } from ".";

const { data } = toRefs(useThrsHistory());

const getSensorValue = <Type extends SensorComponentType, Module extends keyof ThrsDefinitions>([
  _type,
  module,
  field,
]: ModuleField<Type, Module>): Ref<SensorDefinitionMap[Type] | undefined> =>
  computed(
    () =>
      data.value?.modules?.[module]?.sensorValues?.[
        field as keyof ThrsModules[Module]["sensorValues"]
      ],
  );

const getControlValue = <Type extends ControlComponentType, Module extends keyof ThrsDefinitions>([
  _type,
  module,
  field,
]: ModuleField<Type, Module>): Ref<ControlDefinitionMap[Type] | undefined> =>
  computed(
    () =>
      data.value?.modules?.[module]?.controlValues?.[
        field as keyof ThrsModules[Module]["controlValues"]
      ],
  );

createMimicDataProvider({
  getSensorValue,
  getControlValue,
});
</script>

<template>
  <slot />
</template>
