<script setup lang="ts">
import { TimeBasedChart } from "@/@types";
import { isStamped, toTimeSeriesData } from "@/lib/utils";
import { useColorMode } from "@vueuse/core";
import { LineChart } from "echarts/charts";
import { GridComponent, LegendComponent } from "echarts/components";
import { use } from "echarts/core";
import { SVGRenderer } from "echarts/renderers";
import { ECBasicOption, SeriesOption } from "echarts/types/dist/shared";
import { computed, ref, toRefs } from "vue";
import VChart from "vue-echarts";

const props = defineProps<{
  max?: number;
  min?: number;
  series: TimeBasedChart<number>[];
}>();
const { max, series, min } = toRefs(props);

use([SVGRenderer, LineChart, GridComponent, LegendComponent]);

const colorMode = useColorMode();

const seriesOptions = computed<SeriesOption[]>(() =>
  series.value.map((serie) => ({
    name: serie.name,
    smooth: true,
    type: "line",
    showSymbol: false,
    data: serie.data.map((point) => (isStamped(point) ? toTimeSeriesData(point) : point)),
  })),
);

const option = ref<ECBasicOption>({
  animation: false,
  backgroundColor: "transparent",
  grid: {
    left: 0,
    top: 0,
    right: 0,

    tooltip: {
      show: true,
    },
  },
  legend: {
    // show: false,
  },
  xAxis: {
    type: "time",
  },
  yAxis: {
    type: "value",
    min,
    max,
  },
  series: seriesOptions,
});
</script>

<template>
  <v-chart
    class="chart"
    :option="option"
    :theme="colorMode"
    autoresize
  />
</template>
