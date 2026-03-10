<script setup lang="ts">
import { getGaugeRootContext, TICK_OFFSET } from ".";
import GaugeTickComponent from "./GaugeTick.vue";

const { ticks } = getGaugeRootContext();
</script>

<template>
  <g>
    <GaugeTickComponent
      v-for="(tick, index) in ticks"
      :key="`tick-${index}`"
      :value="tick.value!"
      :angle="tick.angle"
      :x="tick.x + TICK_OFFSET * Math.cos(tick.angleInRadians)"
      :y="tick.y + TICK_OFFSET * Math.sin(tick.angleInRadians)"
    />
  </g>
</template>
