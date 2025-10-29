<script setup lang="ts" generic="K extends keyof THRSModules">
import { SimulationComponentType } from "@/@types/thrs";
import { THRSDefinitions, THRSModules } from "@/lib/consts";
import { Client } from "@urql/vue";
import { useIntervalFn } from "@vueuse/core";
import { type Component, computed, ref } from "vue";
import { queryFor, queryPacked } from ".";
import BoundaryControl from "./controls/BoundaryControl.vue";
import PcsControl from "./controls/PcsControl.vue";
import TemperatureControl from "./controls/TemperatureControl.vue";
import ThrustersControl from "./controls/ThrustersControl.vue";

const props = defineProps<{
  module: K;
  simulationControls: THRSDefinitions[K]["simulation"];
  query: string;
  client: Client;
}>();

const COMPONENTS: Record<SimulationComponentType, Component | null> = {
  [SimulationComponentType.Thruster]: ThrustersControl,
  [SimulationComponentType.Boundary]: BoundaryControl,
  [SimulationComponentType.Flow]: null,
  [SimulationComponentType.Temperature]: TemperatureControl,
  [SimulationComponentType.Pcs]: PcsControl,
};

const simulationValuesQuery = queryFor(props.module, "simulation", `inputs { ${props.query} }`);
const simulationValuesFromQuery = queryPacked(props.module, "simulation", simulationValuesQuery);
const simulationValuesFromMutation = ref<THRSModules[K]["simulation"]["inputs"] | null>(null);
const simulationValues = computed(
  () =>
    <THRSModules[K]["simulation"]["inputs"] | undefined>(
      (simulationValuesFromMutation.value ?? simulationValuesFromQuery.value.data?.inputs)
    ),
);

useIntervalFn(
  async () => {
    await simulationValuesFromQuery.value.executeQuery();
    simulationValuesFromMutation.value = null;
  },
  5000,
  { immediateCallback: true },
);

const simulationComponents = computed(() => {
  return Object.entries(props.simulationControls.inputs)
    .map(([key, value]) => ({
      ...value,
      key: key as keyof THRSModules[K]["simulation"]["inputs"],
      component: COMPONENTS[value.componentType],
    }))
    .filter((control) => control.component !== null);
});

const setsimulationValues = (newValues: THRSModules[K]["simulation"]["inputs"]) => {
  simulationValuesFromMutation.value = newValues;
};
</script>
<template>
  <section
    v-if="simulationValues && simulationValuesFromQuery.data?.inputs"
    class="mb-4 grid gap-6 md:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4"
  >
    <component
      :is="control.component"
      v-for="control in simulationComponents"
      :key="control.key"
      :values="simulationValues[control.key]"
      :component-name="control.key"
      :component-type="control.componentType"
      :query="query"
      :module="module"
      @update:control-values="setsimulationValues"
    />
  </section>
</template>
