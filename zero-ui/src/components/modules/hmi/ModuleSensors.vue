<script setup lang="ts">
import { Stamped } from "@/@types/thrs";
import { SENSOR_FIELDS, THRSModules } from "@/lib/consts";
import { Client } from "@urql/vue";
import { useIntervalFn } from "@vueuse/core";
import { computed } from "vue";
import { queryFor, queryPacked } from ".";
import ValueTable from "./ValueTable.vue";

const props = defineProps<{
  module: keyof THRSModules;
  query: string;
  client: Client;
}>();

const FIELDS = Array.from(new Set(Object.values(SENSOR_FIELDS).flat()));

export type FieldName = (typeof FIELDS)[number];
export type FieldEntry = [componentName: string, value: Stamped<string | number | boolean>];
export type FieldValuesTuple = [fieldName: FieldName, entries: FieldEntry[]];

const sensorValuesQuery = queryFor(props.module, "sensorValues", props.query);
const sensorValues = queryPacked(props.module, "sensorValues", sensorValuesQuery);

const extractEntriesByField = <T extends FieldName>(field: T): FieldValuesTuple => {
  if (!sensorValues.value.data) return [field, []];

  const componentsWithField: FieldEntry[] = Object.entries(sensorValues.value.data)
    .filter(([, component]) => field in component)
    .map(([name, component]) => [name, component[field as keyof typeof component]]);

  return [field, componentsWithField];
};

const entriesGroupedByField = computed(() =>
  FIELDS.map(extractEntriesByField).toSorted(([, rowsA], [, rowsB]) => rowsA.length - rowsB.length),
);

useIntervalFn(
  async () => {
    await sensorValues.value.executeQuery();
  },
  5000,
  { immediateCallback: true },
);
</script>
<template>
  <section
    v-if="sensorValues.data"
    class="grid gap-6 lg:grid-cols-2 2xl:grid-cols-3"
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
          v-if="entries"
          :values="entries"
          :format="(value: number) => value.toFixed(2)"
        />
      </p>
    </hgroup>
  </section>
</template>
