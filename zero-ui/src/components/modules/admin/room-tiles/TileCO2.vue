<script setup lang="ts">
import { Room, Units } from "@/@types";
import { CO2_RANGE, CO2_SETPOINT_RANGE, CO2_THRESHOLDS } from "@/lib/consts";
import {
  extractActualCO2,
  formatInt,
  isCO2Control,
  isCO2Sensor,
  useDemoControlValues,
  useDemoSensorValues,
  useThresholds,
} from "@/lib/utils";
import { useHistoryStore } from "@/stores/history";
import AreaChart from "@components/shared/area-chart/AreaChart.vue";
import { ValueTile } from "@components/shared/value-tile";
import { SeriesOption } from "echarts/types/dist/shared";
import { computed } from "vue";

const props = defineProps<{ room: Room }>();

const hasCO2Sensor = computed(() => props.room.roomsSensors.some(isCO2Sensor));
const actualCO2 = computed(() => extractActualCO2(props.room) ?? 0);

const { useSensorHistory, useControlHistory } = useHistoryStore();

const history = useDemoSensorValues(
  () => useSensorHistory(props.room.roomsSensors.find(isCO2Sensor)?.id),
  24,
  { min: CO2_RANGE[0], max: CO2_RANGE[1] },
);

const setpointHistory = useDemoControlValues(
  () => useControlHistory(props.room.roomsControls.find(isCO2Control)?.id),
  24,
  { min: CO2_SETPOINT_RANGE[0], max: CO2_SETPOINT_RANGE[1] },
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

const state = useThresholds(CO2_THRESHOLDS, actualCO2);
</script>

<template>
  <ValueTile
    v-if="hasCO2Sensor"
    :title="room.name"
    :state="state"
  >
    <template #background>
      <AreaChart
        x-axis="time"
        :data="history"
        :min="0"
        :max="CO2_RANGE[1]"
        :thresholds="CO2_THRESHOLDS"
        :extra-series="setpointSeries"
      />
    </template>
    <template #center>
      <span>{{ formatInt(actualCO2) }}</span>
    </template>
    <template #bottom-right>
      <span class="text-rlg text-muted-foreground font-extralight">{{ Units.PPM }}</span>
    </template>
  </ValueTile>
</template>
