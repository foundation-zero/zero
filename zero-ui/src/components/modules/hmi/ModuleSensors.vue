<script setup lang="ts">
import { SensorDefinitions, Stamped } from "@/@types/thrs";
import { SENSOR_FIELDS, THRSModules } from "@/lib/consts";
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
  sensors: SensorDefinitions;
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
  <div v-if="sensorValues.data">
    <header class="mb-2 text-2xl capitalize">{{ t("views.thrs.hmi.sensors") }}</header>
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
            v-if="entries"
            :values="entries"
            :format="(value: number) => value.toFixed(2)"
          />
        </p>
      </hgroup>
    </section>
  </div>
</template>
