<script setup lang="ts">
import { Room } from "@/@types";
import AreaChart from "@/components/ui/area-chart/AreaChart.vue";
import { ValueTile } from "@/components/ui/value-tile";
import { toValueObject, useLiveRandomValues, useThresholds, useTransform } from "@/lib/utils";
import { Droplets } from "lucide-vue-next";
import { computed } from "vue";

const props = defineProps<{ room: Room }>();

const THRESHOLDS: [tempWarm: number, tempHot: number] = [25, 30];
const RANGE = [15, 35];

const history = useTransform(
  useLiveRandomValues(24, {
    min: 18,
    max: 32,
  }),
  toValueObject,
);

const state = useThresholds(
  THRESHOLDS,
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
        :min="RANGE[0]"
        :max="RANGE[1]"
        :thresholds="THRESHOLDS"
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
