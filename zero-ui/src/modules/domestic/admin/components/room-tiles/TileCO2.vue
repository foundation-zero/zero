<script setup lang="ts">
import { CO2_RANGE, CO2_SETPOINT_RANGE, CO2_THRESHOLDS } from "@/modules/domestic/lib/consts";
import { Room, Units, VentilationLog } from "@/modules/domestic/types";
import AreaChart from "@common/components/area-chart/AreaChart.vue";
import { ValueTile } from "@common/components/value-tile";
import {
  extractActualCO2,
  formatInt,
  logToSeries,
  useDemoControlValues,
  useDemoSensorValues,
  useThresholds,
} from "@common/lib/utils";
import { SeriesOption } from "echarts/types/dist/shared";
import { computed } from "vue";

const props = defineProps<{
  room: Room;
  ventilationLog?: VentilationLog[];
}>();

const hasCO2Sensor = computed(() => !!props.room.ventilation);
const actualCO2 = computed(() => extractActualCO2(props.room) ?? 0);

const history = useDemoSensorValues(
  () => computed(() => logToSeries(props.ventilationLog, "actualCo2")),
  24,
  { min: CO2_RANGE[0], max: CO2_RANGE[1] },
);

const setpointHistory = useDemoControlValues(
  () => computed(() => logToSeries(props.ventilationLog, "co2Setpoint")),
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
    :title="room.name!"
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
