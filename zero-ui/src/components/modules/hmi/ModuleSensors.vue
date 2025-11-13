<script
  setup
  lang="ts"
  generic="
    K extends keyof THRSModules,
    Definitions extends SensorDefinitions = THRSModules[K]['sensorValues'],
    Values extends ExtractSensorValues<Definitions> = ExtractSensorValues<Definitions>
  "
>
import { ExtractSensorValues, SensorDefinitions } from "@/@types/thrs";
import { SENSOR_FIELDS, THRSModules } from "@/lib/consts";
import { Client } from "@urql/vue";

import TimeBasedValueChart from "@/components/ui/shared/time-based-chart/TimeBasedValueChart.vue";
import { isNumberChart } from "@/lib/utils";
import { queryDeep, queryFor, useHistory } from ".";

const props = defineProps<{
  module: K;
  sensors: Definitions;
  query: string;
  client: Client;
}>();

const FIELDS = Array.from(new Set(Object.values(SENSOR_FIELDS).flat()));

const sensorValuesQuery = queryFor(props.module, "sensorValues", props.query);
const sensorValues = queryDeep(
  sensorValuesQuery,
  (data) => data?.modules?.[props.module]?.sensorValues as Values | undefined,
);

const { series } = useHistory(sensorValues, FIELDS, `${props.module}:sensors`);
</script>
<template>
  <section
    v-if="sensorValues.data"
    class="grid gap-6 lg:grid-cols-2"
  >
    <template
      v-for="[field, entries] in series"
      :key="field"
    >
      <hgroup
        v-if="entries.length"
        class="bg-background border-border grid rounded-md border"
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
