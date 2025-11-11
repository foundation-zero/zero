<script
  setup
  lang="ts"
  generic="
    K extends keyof THRSModules,
    Definitions extends SimulationDefinitions = THRSModules[K]['simulation']['inputs'],
    Values extends ExtractSimulationValues<Definitions> = ExtractSimulationValues<Definitions>
  "
>
import { ExtractSimulationValues, SimulationDefinitions } from "@/@types/thrs";
import TimeBasedValueChart from "@/components/ui/shared/time-based-chart/TimeBasedValueChart.vue";
import { SIMULATION_FIELDS, THRSModules } from "@/lib/consts";
import { isNumberChart } from "@/lib/utils";
import { Client } from "@urql/vue";
import { queryDeep, queryFor, useHistory } from ".";

const props = defineProps<{
  module: K;
  simulationOutputs: Definitions;
  query: string;
  client: Client;
}>();

const FIELDS = Array.from(new Set(Object.values(SIMULATION_FIELDS).flat()));

const simulationValuesQuery = queryFor(props.module, "simulation", `outputs { ${props.query} }`);
const simulationValues = queryDeep(
  simulationValuesQuery,
  (data) => data?.modules?.[props.module].simulation.outputs as Values | undefined,
);

const { series } = useHistory(simulationValues, FIELDS, `${props.module}:simulation:outputs`);
</script>
<template>
  <section
    v-if="simulationValues.data"
    class="grid gap-6 lg:grid-cols-2"
  >
    <template
      v-for="[field, entries] in series"
      :key="field"
    >
      <hgroup
        v-if="entries.length"
        class="bg-background border-border rounded-md border"
      >
        <header class="p-3 font-semibold capitalize">
          {{ field }}
        </header>
        <p class="h-[400px] grow p-3">
          <TimeBasedValueChart
            v-if="isNumberChart(entries)"
            :series="entries"
          />
        </p>
      </hgroup>
    </template>
  </section>
</template>
