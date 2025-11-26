<script
  setup
  lang="ts"
  generic="
    K extends keyof THRSModules,
    Definitions extends SimulationDefinitions = THRSDefinitions[K]['simulation']['inputs'],
    Values extends ExtractSimulationValues<Definitions> = ExtractSimulationValues<Definitions>
  "
>
import { THRSDefinitions, THRSModules } from "@/modules/thrs/lib/consts";
import {
  ExtractSimulationValues,
  SimulationComponentType,
  SimulationDefinitions,
} from "@/modules/thrs/types";
import { Client } from "@urql/vue";
import { useIntervalFn } from "@vueuse/core";
import { type Component, computed, ref } from "vue";
import { queryDeep, queryFor } from ".";
import BoundaryControl from "./controls/BoundaryControl.vue";
import PcsControl from "./controls/PcsControl.vue";
import TemperatureControl from "./controls/TemperatureControl.vue";
import ThrustersControl from "./controls/ThrustersControl.vue";

const props = defineProps<{
  module: K;
  simulationInputs: Definitions;
  query: string;
  client: Client;
}>();

const COMPONENTS: Record<SimulationComponentType, Component | null> = {
  [SimulationComponentType.Thruster]: ThrustersControl,
  [SimulationComponentType.Boundary]: BoundaryControl,
  [SimulationComponentType.Flow]: null,
  [SimulationComponentType.Temperature]: TemperatureControl,
  [SimulationComponentType.Pcs]: PcsControl,
  [SimulationComponentType.HeatSource]: null,
};

const simulationValuesQuery = queryFor(props.module, "simulation", `inputs { ${props.query} }`);
const simulationValuesFromQuery = queryDeep(
  simulationValuesQuery,
  (data) => data?.modules?.[props.module]?.simulation.inputs as Values | undefined,
);
const simulationValuesFromMutation = ref<Values | null>(null);
const simulationValues = computed(
  () => (simulationValuesFromMutation.value ?? simulationValuesFromQuery.data.value) as Values,
);

useIntervalFn(
  async () => {
    await simulationValuesFromQuery.update();
    simulationValuesFromMutation.value = null;
  },
  5000,
  { immediateCallback: true },
);

const simulationComponents = computed(() => {
  return Object.entries(props.simulationInputs)
    .map(([key, value]) => ({
      ...value,
      key: key as keyof Values,
      component: COMPONENTS[value.componentType],
    }))
    .filter((control) => control.component !== null);
});

const setSimulationValues = (newValues: Values) => {
  simulationValuesFromMutation.value = newValues;
};
</script>
<template>
  <section
    v-if="simulationValues && simulationValuesFromQuery.data.value"
    class="mb-4 grid gap-6 md:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4"
  >
    <template
      v-for="control in simulationComponents"
      :key="control.key"
    >
      <component
        :is="control.component"
        v-if="control.component"
        :values="simulationValues[control.key]"
        :component-name="control.key"
        :component-type="control.componentType"
        :query="query"
        :module="module"
        @update:control-values="setSimulationValues"
      />
    </template>
  </section>
</template>
