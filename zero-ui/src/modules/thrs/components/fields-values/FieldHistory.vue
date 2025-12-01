<script
  setup
  lang="ts"
  generic="
    K extends keyof THRSModules,
    Definitions extends SchemaDefinitions<SchemaDefinition<unknown>>
  "
>
import { THRSModules, THRUSTER_MODES } from "@/modules/thrs/lib/consts";
import { SchemaDefinition, SchemaDefinitions } from "@/modules/thrs/types";

import TimeBasedValueChart from "@/modules/common/components/time-based-chart/TimeBasedValueChart.vue";
import { ChartDataType, SeriesChart } from "@/modules/common/types";
import TimeBasedCategoryChart from "@common/components/time-based-chart/TimeBasedCategoryChart.vue";
import { isBooleanChart, isNumberChart, isStringChart, toCapitalized } from "@common/lib/utils";
import { inject } from "vue";
import { ChartCard, ChartCardContent, ChartCardTitle } from "../chart-card";

const series = inject<SeriesChart<ChartDataType>[]>("fieldSeries")!;
const field = inject<string>("field")!;
</script>
<template>
  <ChartCard
    v-if="isNumberChart(series)"
    class="2xl:col-span-2"
  >
    <ChartCardTitle>{{ field }}</ChartCardTitle>
    <ChartCardContent>
      <TimeBasedValueChart :series="series" />
    </ChartCardContent>
  </ChartCard>
  <template v-else-if="isBooleanChart(series)">
    <ChartCard
      v-for="entry in series"
      :key="entry.name"
      :title="entry.name"
    >
      <ChartCardTitle>{{ entry.name }}</ChartCardTitle>
      <ChartCardContent>
        <TimeBasedCategoryChart
          :series="entry"
          :format="(val) => (val ? 'Active' : 'Inactive')"
          :categories="['Inactive', 'Active']"
        />
      </ChartCardContent>
    </ChartCard>
  </template>
  <template v-else-if="isStringChart(series)">
    <ChartCard
      v-for="entry in series"
      :key="entry.name"
      :title="entry.name"
    >
      <ChartCardTitle>{{ entry.name }}</ChartCardTitle>
      <ChartCardContent>
        <TimeBasedCategoryChart
          :series="entry"
          :format="toCapitalized"
          :categories="THRUSTER_MODES"
        />
      </ChartCardContent>
    </ChartCard>
  </template>
</template>
