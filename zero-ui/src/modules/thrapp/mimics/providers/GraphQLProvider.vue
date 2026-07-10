<script setup lang="ts" generic="K extends keyof THRS['modules']">
import { THRS, ThrsDefinitions, ThrsModules } from "@/modules/thrs/lib/consts.types";
import { useThrsHistory } from "@/modules/thrs/stores/history";
import {
  ControlComponentType,
  ControlDefinitionMap,
  ControllerStateComponentType,
  ControllerStateDefinitionMap,
  ParameterDefinitionMap,
  ParametersType,
  SensorComponentType,
  SensorDefinitionMap,
} from "@/modules/thrs/types";
import { computed, Ref, toRefs, unref } from "vue";
import { createMimicDataProvider, ModuleField } from ".";
import { useAutomaticMode } from "../../state";
import { MimicComponentState } from "../components";

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

const getParameterValue = <Type extends ParametersType, Module extends keyof ThrsDefinitions>([
  _type,
  module,
  field,
]: ModuleField<Type, Module>): Ref<ParameterDefinitionMap[Type] | undefined> =>
  computed(
    () =>
      data.value?.modules?.[module]?.parameters?.[field as keyof ThrsModules[Module]["parameters"]],
  );

const getControllerState = <
  Type extends ControllerStateComponentType,
  Module extends keyof ThrsDefinitions,
>([_type, module, field]: ModuleField<Type, Module>): Ref<
  ControllerStateDefinitionMap[Type] | undefined
> =>
  computed(
    () =>
      data.value?.modules?.[module]?.controllerState?.[
        field as keyof ThrsModules[Module]["controllerState"]
      ],
  );
const isAutomaticMode = useAutomaticMode();

createMimicDataProvider({
  getSensorValue,
  getControlValue,
  getParameterValue,
  getControllerState,
  getComponentState: (state) =>
    computed(() => {
      if (!isAutomaticMode.value) {
        return MimicComponentState.Manual;
      } else {
        return unref(state) ?? MimicComponentState.Normal;
      }
    }),
});
</script>

<template>
  <slot />
</template>
