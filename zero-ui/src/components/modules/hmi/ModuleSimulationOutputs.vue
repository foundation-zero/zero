<script setup lang="ts">
import { Stamped } from "@/@types/thrs";
import { SIMULATION_FIELDS, THRSModules } from "@/lib/consts";
import { Client } from "@urql/vue";
import { useIntervalFn } from "@vueuse/core";
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { queryFor, queryPacked } from ".";
import ValueTable from "./ValueTable.vue";

const { t } = useI18n();

const props = defineProps<{
  module: keyof THRSModules;
  query: string;
  client: Client;
}>();

const FIELDS = Array.from(new Set(Object.values(SIMULATION_FIELDS).flat()));

export type FieldName = (typeof FIELDS)[number];
export type FieldEntry = [componentName: string, value: Stamped<string | number | boolean>];
export type FieldValuesTuple = [fieldName: FieldName, entries: FieldEntry[]];

const simulationValuesQuery = queryFor(props.module, "simulation", `outputs { ${props.query} }`);
const simulationValues = queryPacked(props.module, "simulation", simulationValuesQuery);

const extractEntriesByField = <T extends FieldName>(field: T): FieldValuesTuple => {
  if (!simulationValues.value.data?.outputs) return [field, []];

  const componentsWithField: FieldEntry[] = Object.entries(simulationValues.value.data.outputs)
    .filter(([, component]) => field in component)
    .map(([name, component]) => [name, component[field as keyof typeof component]]);

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
  <div v-if="simulationValues.data">
    <header class="mb-2 text-2xl capitalize">{{ t("views.thrs.hmi.simulation:outputs") }}</header>
    <section class="grid gap-4 md:grid-cols-2 2xl:grid-cols-4">
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
  </div>
</template>
