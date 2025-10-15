<script setup lang="ts" generic="K extends keyof THRSModules">
import { ControlComponentType } from "@/@types/thrs";
import { THRSDefinitions, THRSModules } from "@/lib/consts";
import { Client } from "@urql/vue";
import { useIntervalFn } from "@vueuse/core";
import { type Component, computed, ref } from "vue";
import { useI18n } from "vue-i18n";
import { queryFor, queryPacked } from ".";
import PumpControl from "./controls/PumpControl.vue";
import ValveControl from "./controls/ValveControl.vue";

const { t } = useI18n();

const props = defineProps<{
  module: K;
  controls: THRSDefinitions[K]["controlValues"];
  query: string;
  client: Client;
}>();

const COMPONENTS: Record<ControlComponentType, Component> = {
  [ControlComponentType.Pump]: PumpControl,
  [ControlComponentType.Valve]: ValveControl,
};

const controlValuesQuery = queryFor(props.module, "controlValues", props.query);
const controlValuesFromQuery = queryPacked(props.module, "controlValues", controlValuesQuery);
const controlValuesFromMutation = ref<THRSModules[K]["controlValues"] | null>(null);
const controlValues = computed(
  () =>
    <THRSModules[K]["controlValues"] | undefined>(
      (controlValuesFromMutation.value ?? controlValuesFromQuery.value.data)
    ),
);

useIntervalFn(
  async () => {
    await controlValuesFromQuery.value.executeQuery();
    controlValuesFromMutation.value = null;
  },
  5000,
  { immediateCallback: true },
);

const controlComponents = computed(() => {
  return Object.entries(props.controls).map(([key, value]) => ({
    ...value,
    key: key as keyof THRSModules[K]["controlValues"],
    component: COMPONENTS[value.componentType],
    valveType: value.componentType === ControlComponentType.Valve ? value.valveType : undefined,
  }));
});

const setControlValues = (newValues: THRSModules[K]["controlValues"]) => {
  controlValuesFromMutation.value = newValues;
};
</script>
<template>
  <div v-if="controlValues">
    <header class="mb-2 text-2xl">{{ t("views.thrs.hmi.controls") }}</header>
    <section class="mb-4 grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 2xl:grid-cols-6">
      <div
        v-for="control in controlComponents"
        :key="control.key"
      >
        <component
          :is="control.component"
          v-if="control.component && controlValuesFromQuery.data?.[control.key]"
          :control-values="controlValues[control.key]"
          :component-name="control.key"
          :component-type="control.componentType"
          :control-values-query="query"
          :yard-tag="control.yardTag"
          :valve-type="control.valveType"
          :module="module"
          @update:control-values="setControlValues"
        />
      </div>
    </section>
  </div>
</template>
