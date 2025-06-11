<script setup lang="ts">
import { Room } from "@/@types";
import { TEMPERATURE_RANGE, TEMPERATURE_THRESHOLDS } from "@/lib/consts";
import { toValueObject, useLiveRandomValues, useThresholds, useTransform } from "@/lib/utils";
import AreaChart from "@components/shared/area-chart/AreaChart.vue";
import { ValueTile } from "@components/shared/value-tile";
import { SeriesOption } from "echarts/types/dist/shared";
import { Droplets } from "lucide-vue-next";
import { computed } from "vue";

const props = defineProps<{ room: Room }>();

const history = useTransform(
  useLiveRandomValues(24, {
    min: 18,
    max: 32,
  }),
  toValueObject,
);

const setpointHistory = useTransform(
  useLiveRandomValues(24, {
    min: 20,
    max: 23,
  }),
  toValueObject,
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

const state = useThresholds(
  TEMPERATURE_THRESHOLDS,
  computed(() => props.room.actualTemperature),
);
</script>

<template>
  <ValueTile
    :title="room.name"
    :state="state"
  >
    <template #background>
      <AreaChart
        :data="history"
        :min="TEMPERATURE_RANGE[0]"
        :max="TEMPERATURE_RANGE[1]"
        :thresholds="TEMPERATURE_THRESHOLDS"
        :extra-series="setpointSeries"
      >
        <template #unit>
          <sup class="text-r2xs font-extralight">&deg;</sup>
        </template>
      </AreaChart>
    </template>
    <template #center>
      <span>{{ room.actualTemperature.toFixed(0) }}</span>
      <sup class="top-[-0.3em] text-rxs font-extralight">&deg;</sup>
    </template>

    <template #bottom-left>
      <Droplets class="inline h-[1em] w-[1em]" />
      <span>
        <span class="ml-[0.5em] font-extrabold">{{ room.actualHumidity.toFixed(0) }}</span>
        <span class="ml-[0.25em] text-rsm font-extralight">&percnt;</span>
      </span>
    </template>

    <template #bottom-right>
      <span>
        <span class="text-rsm font-light">Set to</span>
        <span class="ml-[0.25em] font-extrabold">
          {{ room.temperatureSetpoint }}
        </span>
        <sup class="font-extralight">&deg;</sup>
      </span>
    </template>
  </ValueTile>
</template>
