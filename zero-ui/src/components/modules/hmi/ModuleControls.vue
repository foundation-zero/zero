<script setup lang="ts" generic="K extends keyof THRSModules">
import { ControlComponentType } from "@/@types/thrs";
import { THRSDefinitions, THRSModules } from "@/lib/consts";
import { useSimulationStore } from "@/stores/simulation";
import { Client } from "@urql/vue";
import { useIntervalFn } from "@vueuse/core";
import { type Component, computed, ref, toRefs } from "vue";
import { queryFor, queryPacked } from ".";
import PumpControl from "./controls/PumpControl.vue";
import ValveControl from "./controls/ValveControl.vue";

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

const { control: controlData } = toRefs(useSimulationStore());

const controlsDisabled = computed(() => controlData.value?.control.automatic === true);

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
  <section
    v-if="controlValues"
    class="mb-4 grid gap-6 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4"
    :class="{ 'pointer-events-none cursor-not-allowed opacity-50': controlsDisabled }"
  >
    <template
      v-for="control in controlComponents"
      :key="control.key"
    >
      <component
        :is="control.component"
        v-if="control.component && controlValuesFromQuery.data?.[control.key]"
        :values="controlValues[control.key]"
        :component-name="control.key"
        :component-type="control.componentType"
        :query="query"
        :yard-tag="control.yardTag"
        :valve-type="control.valveType"
        :module="module"
        @update:control-values="setControlValues"
      />
    </template>
  </section>
</template>
