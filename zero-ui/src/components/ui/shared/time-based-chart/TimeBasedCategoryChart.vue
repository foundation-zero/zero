<script setup lang="ts" generic="T extends ChartDataType, V extends string">
import { ChartDataType, SeriesChart, StampedChart, TimeSeriesData } from "@/@types";
import { cast } from "@/lib/utils";
import { useColorMode } from "@vueuse/core";
import { CustomSeriesRenderItem, EChartsOption } from "echarts";
import { CustomChart, LineChart } from "echarts/charts";
import {
  DataZoomComponent,
  GridComponent,
  LegendComponent,
  TitleComponent,
  TooltipComponent,
} from "echarts/components";
import * as echarts from "echarts/core";
import { use } from "echarts/core";
import { SVGRenderer } from "echarts/renderers";
import { computed } from "vue";
import VChart from "vue-echarts";

use([
  SVGRenderer,
  LineChart,
  GridComponent,
  LegendComponent,
  TooltipComponent,
  CustomChart,
  TitleComponent,
  DataZoomComponent,
]);

const colorMode = useColorMode();

type CategoryDefinition = {
  value: [categoryIndex: number, start: number, end: number, duration: number];
  itemStyle: {
    color: string;
  };
};

type Coords = {
  x: number;
  y: number;
  width: number;
  height: number;
};

const props = defineProps<
  {
    categories: V[];
  } & (
    | {
        series: StampedChart<V>;
        format?: never;
      }
    | {
        series: StampedChart<T>;
        format: (data: T) => V;
      }
  )
>();

const categoryColours = ["#7b9ce1", "#bd6d6c", "#75d874", "#e0bc78", "#dc77dc", "#72b362"];

const series = computed<SeriesChart<number>>(() => {
  const dataPoints: TimeSeriesData<number>[] = props.series.data.map(({ timestamp, value }) => {
    const category = typeof value === "string" ? (value as V) : props.format!(value);

    return [new Date(timestamp), props.categories.indexOf(category)];
  });

  return {
    name: props.series.name,
    data: dataPoints,
  };
});

const startTime = computed<number>(() => {
  if (series.value.data.length === 0) {
    return Date.now();
  }

  const [time] = series.value.data[0];

  return +time;
});

const data = computed<CategoryDefinition[]>(() => {
  if (series.value.data.length === 0) {
    return [];
  }

  let [startTime, category] = series.value.data[0];
  const [endTime] = series.value.data[series.value.data.length - 1];

  let baseTime = +startTime;

  const toItem = (end: number): CategoryDefinition => ({
    value: [category, baseTime, end, end - baseTime],
    itemStyle: {
      color: categoryColours[category % categoryColours.length],
    },
  });

  const data = series.value.data.reduce((data, [timestamp, categoryIndex]) => {
    // To render the categories, we only record changes in category value over time.
    if (category !== categoryIndex) {
      data.push(toItem(+timestamp));
      category = categoryIndex;
      baseTime = +timestamp;
    }

    return data;
  }, [] as CategoryDefinition[]);

  // This will add the last category if the final entry did not change the category.
  if (baseTime !== +endTime) {
    data.push(toItem(+endTime));
  }

  return data;
});

// This render function was provided by the ECharts documentation and refactored to add types.
// https://echarts.apache.org/en/option.html#series-custom.renderItem
const renderItem: CustomSeriesRenderItem = (params, api) => {
  const categoryIndex = Number(api.value(0));
  var start = api.coord([api.value(1), categoryIndex]);
  var end = api.coord([api.value(2), categoryIndex]);
  var height = (<number[]>api.size!([0, 1]))[1] * 0.6;
  const coordSys = cast<Coords>(params.coordSys);
  var rectShape = echarts.graphic.clipRectByRect(
    {
      x: start[0],
      y: start[1] - height / 2,
      width: end[0] - start[0],
      height: height,
    },
    {
      x: coordSys.x,
      y: coordSys.y,
      width: coordSys.width,
      height: coordSys.height,
    },
  );
  return (
    rectShape && {
      type: "rect",
      transition: ["shape"],
      shape: rectShape,
      style: {
        fill: api.visual("color"),
      },
    }
  );
};

const option = computed<EChartsOption>(() => ({
  backgroundColor: "transparent",
  grid: {
    left: 32,
    top: 32,
    right: 32,
    bottom: 32,
    tooltip: {
      show: true,
    },
  },
  legend: {
    show: false,
  },
  xAxis: {
    min: startTime.value,
    scale: true,
    type: "time",
  },
  yAxis: {
    data: props.categories,
  },
  series: [
    {
      type: "custom",
      renderItem,
      encode: {
        x: [1, 2],
        y: 0,
      },
      data: data.value,
    },
  ],
}));
</script>

<template>
  <v-chart
    class="chart"
    :option="option"
    :theme="colorMode"
    autoresize
  />
</template>
