<script setup lang="ts">
import { Room } from "@/@types";
import { HUMIDITY_RANGE, HUMIDITY_SETPOINT_RANGE, HUMIDITY_THRESHOLDS } from "@/lib/consts";
import {
  extractActualHumidity,
  isHumidityControl,
  isHumiditySensor,
  useDemoControlValues,
  useDemoSensorValues,
  useSafeRange,
} from "@/lib/utils";
import { useHistoryStore } from "@/stores/history";
import AreaChart from "@components/shared/area-chart/AreaChart.vue";
import { ValueTile } from "@components/shared/value-tile";
import { SeriesOption } from "echarts/types/dist/shared";
import { computed } from "vue";

const props = defineProps<{ room: Room }>();

const hasHumiditySensor = computed(() => props.room.roomsSensors.some(isHumiditySensor));
const actualHumidity = computed(() => extractActualHumidity(props.room) ?? 0);

const { useSensorHistory, useControlHistory } = useHistoryStore();

const history = useDemoSensorValues(
  () => useSensorHistory(props.room.roomsSensors.find(isHumiditySensor)?.id),
  24,
  { min: HUMIDITY_RANGE[0], max: HUMIDITY_RANGE[1] },
);

const setpointHistory = useDemoControlValues(
  () => useControlHistory(props.room.roomsControls.find(isHumidityControl)?.id),
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
    :title="room.name"
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
