<script setup lang="ts">
import { SolarPanelStringProps } from ".";
import { SolarPanel } from "../solar-panel";

defineProps<SolarPanelStringProps>();
</script>

<template>
  <g data-slot="solar-panel-string">
    <SolarPanel
      v-for="panel in panels"
      :key="`${panel.x}-${panel.y}`"
      v-bind="panel"
      :yield-ratio="yieldRatio"
    />

    <rect
      v-if="'width' in frame"
      :x="frame.x"
      :y="frame.y"
      :width="frame.width"
      :height="frame.height"
      class="fill-muted/50 stroke-brand-a-500"
    />
    <path
      v-else
      :d="frame.d"
      class="fill-muted/50 stroke-brand-a-500"
    />

    <text
      v-if="label"
      :x="label.x"
      :y="label.y"
      :transform="label.vertical ? `rotate(-90 ${label.x} ${label.y})` : undefined"
      text-anchor="middle"
      dominant-baseline="central"
      class="fill-foreground text-2xs"
    >
      <slot />
    </text>
  </g>
</template>
