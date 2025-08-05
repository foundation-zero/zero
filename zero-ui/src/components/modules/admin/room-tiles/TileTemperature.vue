<script setup lang="ts">
import { Room } from "@/@types";
import {
  TEMPERATURE_RANGE,
  TEMPERATURE_SETPOINT_RANGE,
  TEMPERATURE_THRESHOLDS,
} from "@/lib/consts";
import {
  extractActualHumidity,
  extractActualTemperature,
  extractTemperatureSetpoint,
  isTemperatureControl,
  isTemperatureSensor,
  useDemoControlValues,
  useDemoSensorValues,
  useThresholds,
} from "@/lib/utils";
import { useHistoryStore } from "@/stores/history";
import AreaChart from "@components/shared/area-chart/AreaChart.vue";
import { ValueTile } from "@components/shared/value-tile";
import { SeriesOption } from "echarts/types/dist/shared";
import { Droplets } from "lucide-vue-next";
import { computed } from "vue";
import { useI18n } from "vue-i18n";

const props = defineProps<{ room: Room }>();

const { useSensorHistory, useControlHistory } = useHistoryStore();

const history = useDemoSensorValues(
  () => useSensorHistory(props.room.roomsSensors.find(isTemperatureSensor)?.id),
  24,
  { min: TEMPERATURE_RANGE[0], max: TEMPERATURE_RANGE[1] },
);

const setpointHistory = useDemoControlValues(
  () => useControlHistory(props.room.roomsControls.find(isTemperatureControl)?.id),
  24,
  { min: TEMPERATURE_SETPOINT_RANGE[0], max: TEMPERATURE_SETPOINT_RANGE[1] },
);

const hasTemperatureSensor = computed(() => props.room.roomsSensors.some(isTemperatureSensor));
const actualTemperature = computed(() => extractActualTemperature(props.room) ?? 0);
const actualHumidity = computed(() => extractActualHumidity(props.room) ?? 0);
const temperatureSetpoint = computed(() => extractTemperatureSetpoint(props.room) ?? 0);

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

const state = useThresholds(TEMPERATURE_THRESHOLDS, actualTemperature);

const { t } = useI18n();
</script>

<template>
  <ValueTile
    v-if="hasTemperatureSensor"
    :title="room.name"
    :state="state"
  >
    <template #background>
      <AreaChart
        :data="history"
        x-axis="time"
        :min="TEMPERATURE_RANGE[0]"
        :max="TEMPERATURE_RANGE[1]"
        :thresholds="TEMPERATURE_THRESHOLDS"
        :extra-series="setpointSeries"
      >
        <template #unit> <sup class="text-r2xs font-extralight">&deg;</sup> </template>
      </AreaChart>
    </template>
    <template #center>
      <span>{{ actualTemperature.toFixed(0) }}</span>
      <sup class="text-rxs top-[-0.3em] font-extralight">&deg;</sup>
    </template>
    <template #bottom-left>
      <Droplets class="inline h-[1em] w-[1em]" />
      <span>
        <span class="ml-[0.5em] font-extrabold">{{ actualHumidity.toFixed(0) }}</span>
        <span class="text-rsm ml-[0.25em] font-extralight">&percnt;</span>
      </span>
    </template>
    <template #bottom-right>
      <span>
        <span class="text-rsm font-light">{{ t("views.ac.setTo") }}</span>
        <span class="ml-[0.25em] font-extrabold"> {{ temperatureSetpoint }} </span>
        <sup class="font-extralight">&deg;</sup>
      </span>
    </template>
  </ValueTile>
</template>
