<script setup lang="ts">
import { Room } from "@/@types";
import { HUMIDITY_RANGE, HUMIDITY_THRESHOLDS } from "@/lib/consts";
import { toValueObject, useLiveRandomValues, useSafeRange, useTransform } from "@/lib/utils";
import AreaChart from "@components/shared/area-chart/AreaChart.vue";
import { ValueTile } from "@components/shared/value-tile";
import { computed } from "vue";

const props = defineProps<{ room: Room }>();

const history = useTransform(
  useLiveRandomValues(24, {
    min: HUMIDITY_RANGE[0],
    max: HUMIDITY_RANGE[1],
  }),
  toValueObject,
);

const state = useSafeRange(
  HUMIDITY_THRESHOLDS,
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
        :min="HUMIDITY_RANGE[0]"
        :max="HUMIDITY_RANGE[1]"
        :thresholds="HUMIDITY_THRESHOLDS"
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
