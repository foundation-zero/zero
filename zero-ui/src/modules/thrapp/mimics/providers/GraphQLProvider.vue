<script setup lang="ts" generic="K extends keyof THRS['modules']">
import { THRS, ThrsModules } from "@/modules/thrs/lib/consts.types";
import { useThrsHistory } from "@/modules/thrs/stores/history";
import { StringKeys } from "@/modules/thrs/types";
import { computed, Ref, toRefs } from "vue";
import { createMimicDataProvider } from ".";

const { data } = toRefs(useThrsHistory());

const getSensorValue = <
  Module extends keyof ThrsModules,
  Field extends keyof StringKeys<ThrsModules[Module]["sensorValues"]>,
>(
  module: Module,
  field: Field,
): Ref<ThrsModules[Module]["sensorValues"][Field] | undefined> =>
  computed(() => data.value?.modules?.[module]?.sensorValues?.[field]);

const getControlValue = <
  Module extends keyof ThrsModules,
  Field extends keyof StringKeys<ThrsModules[Module]["controlValues"]>,
>(
  module: Module,
  field: Field,
): Ref<ThrsModules[Module]["controlValues"][Field] | undefined> =>
  computed(() => data.value?.modules?.[module]?.controlValues?.[field]);

createMimicDataProvider({
  getSensorValue,
  getControlValue,
});
</script>

<template>
  <slot />
</template>
