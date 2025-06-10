<script setup lang="ts">
import { Room, Units } from "@/@types";
import AreaChart from "@/components/ui/area-chart/AreaChart.vue";
import { ValueTile } from "@/components/ui/value-tile";
import { CO2_RANGE, CO2_THRESHOLDS } from "@/lib/consts";
import {
  formatInt,
  toValueObject,
  useLiveRandomValues,
  useThresholds,
  useTransform,
} from "@/lib/utils";
import { computed } from "vue";

const props = defineProps<{ room: Room }>();

const history = useTransform(
  useLiveRandomValues(24, { min: CO2_RANGE[0], max: CO2_RANGE[1] }),
  toValueObject,
);

const state = useThresholds(
  CO2_THRESHOLDS,
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
        :max="CO2_RANGE[1]"
        :thresholds="CO2_THRESHOLDS"
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
