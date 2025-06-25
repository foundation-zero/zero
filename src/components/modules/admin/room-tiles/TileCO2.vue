<script setup lang="ts">
import { Room, Units } from "@/@types";
import { CO2_RANGE, CO2_THRESHOLDS } from "@/lib/consts";
import {
  extractActualCO2,
  formatInt,
  isCO2Sensor,
  toValueObject,
  useLiveRandomValues,
  useThresholds,
  useTransform,
} from "@/lib/utils";
import AreaChart from "@components/shared/area-chart/AreaChart.vue";
import { ValueTile } from "@components/shared/value-tile";
import { computed } from "vue";

const props = defineProps<{ room: Room }>();

const hasCO2Sensor = computed(() => props.room.roomsSensors.some(isCO2Sensor));
const actualCO2 = computed(() => extractActualCO2(props.room) ?? 0);

const history = useTransform(
  useLiveRandomValues(24, { min: CO2_RANGE[0], max: CO2_RANGE[1] }),
  toValueObject,
);

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
        :data="history"
        :min="0"
        :max="CO2_RANGE[1]"
        :thresholds="CO2_THRESHOLDS"
      />
    </template>
    <template #center>
      <span>{{ formatInt(actualCO2) }}</span>
    </template>
    <template #bottom-right>
      <span class="text-rlg font-extralight">{{ Units.PPM }}</span>
    </template>
  </ValueTile>
</template>
