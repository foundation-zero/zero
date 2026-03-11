<script setup lang="ts">
import {
  createGaugeContext,
  GAUGE_HEIGHT,
  GAUGE_PADDING,
  GAUGE_WIDTH,
  GaugePoints,
  GaugeRootProps,
  GaugeTargetRange,
  GaugeTicks,
  provideGaugeRootContext,
} from ".";

const props = defineProps<GaugeRootProps>();

provideGaugeRootContext(createGaugeContext(props));
</script>

<template>
  <svg
    :width="GAUGE_WIDTH"
    :height="GAUGE_HEIGHT"
    :viewBox="`0 ${GAUGE_PADDING} ${GAUGE_WIDTH} ${GAUGE_HEIGHT}`"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <GaugePoints />
    <GaugeTicks />
    <GaugeTargetRange />
  </svg>
</template>
