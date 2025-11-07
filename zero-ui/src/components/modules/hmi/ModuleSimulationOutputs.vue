<script
  setup
  lang="ts"
  generic="
    K extends keyof THRSModules,
    Definitions extends SimulationDefinitions = THRSModules[K]['simulation']['inputs'],
    Values extends ExtractSimulationValues<Definitions> = ExtractSimulationValues<Definitions>
  "
>
import { ExtractSimulationValues, SimulationDefinitions, Stamped } from "@/@types/thrs";
import { SIMULATION_FIELDS, THRSModules } from "@/lib/consts";
import { tuple } from "@/lib/utils";
import { Client } from "@urql/vue";
import { useIntervalFn } from "@vueuse/core";
import { computed } from "vue";
import { queryFor, queryPacked } from ".";
import ValueTable from "./ValueTable.vue";

const props = defineProps<{
  module: keyof THRSModules;
  simulationOutputs: Definitions;
  query: string;
  client: Client;
}>();

const FIELDS = Array.from(new Set(Object.values(SIMULATION_FIELDS).flat()));

type FieldName = (typeof FIELDS)[number];
type FieldEntry = [componentName: string, value: Stamped<string | number | boolean>];
type FieldValuesTuple = [fieldName: FieldName, entries: FieldEntry[]];

const simulationValuesQuery = queryFor(props.module, "simulation", `outputs { ${props.query} }`);
const simulationValues = queryPacked(
  simulationValuesQuery,
  (data) => data?.modules?.[props.module]?.simulation.outputs as Values | undefined,
);

const extractEntriesByField = <T extends FieldName>(field: T): FieldValuesTuple => {
  if (!simulationValues.value.data) return [field, []];

  const componentsWithField: FieldEntry[] = Object.keys(props.simulationOutputs)
    .map((name) => tuple(name as keyof Values, simulationValues.value.data![name as keyof Values]))
    .filter(([, component]) => field in component)
    .map(([name]) => [String(name), simulationValues.value.data![name][field]]);

  return [field, componentsWithField];
};

const entriesGroupedByField = computed(() =>
  FIELDS.map(extractEntriesByField)
    .filter(([, rows]) => rows.length > 0)
    .toSorted(([, rowsA], [, rowsB]) => rowsA.length - rowsB.length),
);

useIntervalFn(
  async () => {
    await simulationValues.value.executeQuery();
  },
  5000,
  { immediateCallback: true },
);
</script>
<template>
  <section
    v-if="simulationValues.data"
    class="grid gap-6 lg:grid-cols-2"
  >
    <hgroup
      v-for="[field, entries] in entriesGroupedByField"
      :key="field"
      class="bg-background border-border rounded-md border"
    >
      <header class="p-3 font-semibold capitalize">
        {{ field }}
      </header>
      <p>
        <ValueTable
          :values="entries"
          :format="(value: number) => value.toFixed(2)"
        />
      </p>
    </hgroup>
  </section>
</template>
