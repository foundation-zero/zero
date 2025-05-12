<script setup lang="ts">
import { Room } from "@/@types";
import AreaChart from "@/components/ui/area-chart/AreaChart.vue";
import { ValueTile } from "@/components/ui/value-tile";
import { toValueObject, useLiveRandomValues, useSafeRange, useTransform } from "@/lib/utils";
import { computed } from "vue";

const props = defineProps<{ room: Room }>();

const THRESHOLDS: [humidityLow: number, humidityHigh: number] = [35, 60];
const RANGE = [30, 80];

const history = useTransform(
  useLiveRandomValues(24, {
    min: RANGE[0],
    max: RANGE[1],
  }),
  toValueObject,
);

const state = useSafeRange(
  THRESHOLDS,
  computed(() => props.room.actualHumidity),
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
          <span class="ml-[0.2em] text-rxs font-extralight">&percnt;</span>
        </template>
      </AreaChart>
    </template>
    <template #center>
      <span>{{ room.actualHumidity.toFixed(0) }}</span>
      <span class="ml-[0.25em] text-r2xs font-extralight">&percnt;</span>
    </template>
  </ValueTile>
</template>
