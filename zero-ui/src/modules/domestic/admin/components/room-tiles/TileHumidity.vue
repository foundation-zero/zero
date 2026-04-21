<script setup lang="ts">
import {
  HUMIDITY_RANGE,
  HUMIDITY_SETPOINT_RANGE,
  HUMIDITY_THRESHOLDS,
} from "@/modules/domestic/lib/consts";
import { Room } from "@/modules/domestic/types";
import AreaChart from "@common/components/area-chart/AreaChart.vue";
import { ValueTile } from "@common/components/value-tile";
import {
  extractActualHumidity,
  hasHumidityControl,
  logToSeries,
  useDemoControlValues,
  useDemoSensorValues,
  useSafeRange,
} from "@common/lib/utils";
import { SeriesOption } from "echarts/types/dist/shared";
import { computed } from "vue";

const props = defineProps<{
  room: Room;
  humidityLog?: { timestamp: Date; actualHumidity: number; humiditySetpoint: number }[];
}>();

const hasHumiditySensor = computed(() => hasHumidityControl(props.room));
const actualHumidity = computed(() => extractActualHumidity(props.room) ?? 0);

const history = useDemoSensorValues(
  () => computed(() => logToSeries(props.humidityLog, "actualHumidity")),
  24,
  { min: HUMIDITY_RANGE[0], max: HUMIDITY_RANGE[1] },
);

const setpointHistory = useDemoControlValues(
  () => computed(() => logToSeries(props.humidityLog, "humiditySetpoint")),
  24,
  { min: HUMIDITY_SETPOINT_RANGE[0], max: HUMIDITY_SETPOINT_RANGE[1] },
);

const setpointSeries = computed<SeriesOption[]>(() => [
  {
    type: "line",
    data: setpointHistory.value,
    showSymbol: false,
    lineStyle: {
      width: 1,
      color: "currentColor",
      type: "dashed",
    },
  },
]);

const state = useSafeRange(HUMIDITY_THRESHOLDS, actualHumidity);
</script>

<template>
  <ValueTile
    v-if="hasHumiditySensor"
    :title="room.name!"
    :state="state"
  >
    <template #background>
      <AreaChart
        x-axis="time"
        :data="history"
        :min="HUMIDITY_RANGE[0]"
        :max="HUMIDITY_RANGE[1]"
        :thresholds="HUMIDITY_THRESHOLDS"
        :extra-series="setpointSeries"
      >
        <template #unit>
          <span class="text-rxs ml-[0.2em] font-extralight">&percnt;</span>
        </template>
      </AreaChart>
    </template>
    <template #center>
      <span>{{ actualHumidity.toFixed(0) }}</span>
      <span class="text-r2xs text-muted-foreground ml-[0.25em] font-extralight">&percnt;</span>
    </template>
  </ValueTile>
</template>
