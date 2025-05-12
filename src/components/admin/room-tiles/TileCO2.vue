<script setup lang="ts">
import { Room, Units } from "@/@types";
import AreaChart from "@/components/ui/area-chart/AreaChart.vue";
import { ValueTile } from "@/components/ui/value-tile";
import {
  formatInt,
  toValueObject,
  useLiveRandomValues,
  useThresholds,
  useTransform,
} from "@/lib/utils";
import { computed } from "vue";

const props = defineProps<{ room: Room }>();

const THRESHOLDS: [warning: number, critical: number] = [1000, 2000];
const RANGE = [400, 2500];

const history = useTransform(
  useLiveRandomValues(24, { min: RANGE[0], max: RANGE[1] }),
  toValueObject,
);

const state = useThresholds(
  THRESHOLDS,
  computed(() => props.room.actualCO2),
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
        :min="0"
        :max="RANGE[1]"
        :thresholds="THRESHOLDS"
      />
    </template>
    <template #center>
      <span>{{ formatInt(room.actualCO2) }}</span>
    </template>
    <template #bottom-right>
      <span class="text-rlg font-extralight">{{ Units.PPM }}</span>
    </template>
  </ValueTile>
</template>
