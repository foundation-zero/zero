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

import TimeBasedCategoryChart from "@/components/ui/shared/time-based-chart/TimeBasedCategoryChart.vue";
import TimeBasedValueChart from "@/components/ui/shared/time-based-chart/TimeBasedValueChart.vue";
import { isBooleanChart, isNumberChart } from "@/lib/utils";
import { queryDeep, queryFor, useHistory } from ".";
import ChartCard from "./ChartCard.vue";

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
      <ChartCard
        v-if="isNumberChart(entries)"
        :title="field"
      >
        <TimeBasedValueChart :series="entries" />
      </ChartCard>
      <template v-else-if="isBooleanChart(entries)">
        <ChartCard
          v-for="entry in entries"
          :key="entry.name"
          :title="`${field} : ${entry.name}`"
        >
          <TimeBasedCategoryChart
            :series="entry"
            :format="(val) => (val ? 'Active' : 'Inactive')"
            :categories="['Inactive', 'Active']"
          />
        </ChartCard>
      </template>
    </template>
  </section>
</template>
