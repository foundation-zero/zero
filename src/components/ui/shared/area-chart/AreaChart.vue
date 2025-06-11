<script setup lang="ts">
import { NumValueObject } from "@/@types";
import { formatInt } from "@/lib/utils";
import { useColorMode } from "@vueuse/core";
import { LineChart } from "echarts/charts";
import { GridComponent, LegendComponent } from "echarts/components";
import { use } from "echarts/core";
import { SVGRenderer } from "echarts/renderers";
import { ECBasicOption, SeriesOption } from "echarts/types/dist/shared";
import { computed, ref, toRefs } from "vue";
import VChart from "vue-echarts";

const props = defineProps<{
  max: number;
  min: number;
  data: NumValueObject[];
  thresholds?: number[];
  extraSeries?: SeriesOption[];
}>();
const { max, data, min } = toRefs(props);
const sortedThresholds = computed(() => props.thresholds?.toSorted((a, b) => a - b) ?? []);
const relativeThresholds = computed(() =>
  sortedThresholds.value.map(
    (threshold) => ((threshold - props.min) / (props.max - props.min)) * 100,
  ),
);

use([SVGRenderer, LineChart, GridComponent, LegendComponent]);

const colorMode = useColorMode();

const series = computed<SeriesOption[]>(() => {
  const areaChart: SeriesOption = {
    smooth: true,
    type: "line",
    showSymbol: false,
    data: data.value,
    lineStyle: {
      width: 0,
    },
    areaStyle: {
      color: "currentColor",
      opacity: 0.2,
    },
  };

  return [areaChart, ...(props.extraSeries ?? [])];
});

const option = ref<ECBasicOption>({
  animation: false,
  backgroundColor: "transparent",
  grid: {
    left: -6,
    top: 0,
    right: -6,
    bottom: 0,
    tooltip: {
      show: true,
    },
  },
  legend: {
    show: false,
  },
  xAxis: {
    type: "category",
    show: false,
  },
  yAxis: {
    type: "value",
    min,
    max,
    splitLine: {
      show: false,
    },
    nameTextStyle: {
      show: false,
    },
    axisLabel: {
      show: false,
    },
  },
  series,
});
</script>

<template>
  <v-chart
    class="chart"
    :option="option"
    :theme="colorMode"
    autoresize
  >
  </v-chart>
  <div
    v-if="thresholds"
    class="absolute left-0 top-0 h-full w-full"
  >
    <span
      v-for="(threshold, i) in sortedThresholds"
      :key="threshold"
      :style="{
        bottom: `${relativeThresholds[i]}%`,
      }"
      class="absolute w-full border-b border-dashed border-primary/35 p-0.5 text-right text-rsm font-light text-primary/80"
    >
      <span>{{ formatInt(threshold) }}</span>
      <slot name="unit" />
    </span>
  </div>
</template>
