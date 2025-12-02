<script setup lang="ts">
import { isStamped, toTimeSeriesData } from "@common/lib/utils";
import { SeriesChart, StampedChart } from "@common/types";
import { useColorMode } from "@vueuse/core";
import { LineChart } from "echarts/charts";
import { GridComponent, LegendComponent } from "echarts/components";
import { use } from "echarts/core";
import { SVGRenderer } from "echarts/renderers";
import { ECBasicOption, SeriesOption } from "echarts/types/dist/shared";
import { computed, ref, toRefs } from "vue";
import VChart from "vue-echarts";
import { ResizeRemount } from "../resize-remount";

const props = defineProps<{
  max?: number;
  min?: number;
  series: StampedChart<number>[] | SeriesChart<number>[];
}>();
const { max, series, min } = toRefs(props);

use([SVGRenderer, LineChart, GridComponent, LegendComponent]);

const seriesOptions = computed<SeriesOption[]>(() =>
  series.value.map((serie) => ({
    name: serie.name,
    smooth: true,
    type: "line",
    showSymbol: false,
    data: serie.data.map((point) => (isStamped(point) ? toTimeSeriesData(point) : point)),
  })),
);

const colorMode = useColorMode();

const option = ref<ECBasicOption>({
  animation: true,
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
    show: true,
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
  <ResizeRemount>
    <VChart
      :option="option"
      :theme="colorMode"
      autoresize
    />
  </ResizeRemount>
</template>
