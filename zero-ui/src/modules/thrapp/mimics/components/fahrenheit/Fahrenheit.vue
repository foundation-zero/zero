<script setup lang="ts">
import { FAHRENHEIT_HEIGHT, FAHRENHEIT_WIDTH } from ".";
import { MimicComponentBaseProps } from "..";
import MimicComponent from "../MimicComponent.vue";

const props = defineProps<MimicComponentBaseProps>();
</script>

<template>
  <MimicComponent
    v-slot="{ stateColor, strokeWidth }"
    :width="FAHRENHEIT_WIDTH"
    :height="FAHRENHEIT_HEIGHT"
    v-bind="props"
  >
    <rect
      x="0.5"
      y="0.5"
      :width="FAHRENHEIT_WIDTH - 1"
      :height="FAHRENHEIT_HEIGHT - 1"
      class="fill-background"
      :stroke="stateColor"
      :stroke-width="strokeWidth"
    />

    <!-- High, medium and low temperature circuits, open where they leave the unit. -->
    <g
      class="stroke-flows-pipe"
      stroke-linejoin="round"
    >
      <path d="M295.6 103.96H37.83V213.96H295.6" />
      <path d="M0.99 238.42H270.39V348.42H0.99" />
      <path d="M295.52 373.13H31.5V483.13H295.52" />
    </g>

    <!-- Heat pipes between the circuits. -->
    <g
      class="stroke-constructive"
      stroke-width="2"
      stroke-linejoin="round"
    >
      <path
        transform="translate(82.34 220.98)"
        d="M0.928477 11L4.92848 1L8.92848 11L12.9285 1L16.9285 11L20.9285 1L24.9285 11L28.9285 1L32.7081 11L36.7081 1L40.7081 11L44.7081 1L48.7081 11L52.7081 1L56.7081 11L60.7081 1L64.7081 11M64.8186 11L68.8186 1L72.8186 11L76.8186 1L80.8186 11L84.8186 1L88.8186 11L92.8186 1L96.5982 11L100.598 1L104.598 11L108.598 1L112.598 11L116.598 1L120.598 11L124.598 1L128.598 11"
      />
      <path
        transform="translate(211.87 356.42) scale(-1 1)"
        d="M0.928477 11L4.92848 1L8.92848 11L12.9285 1L16.9285 11L20.9285 1L24.9285 11L28.9285 1L32.7081 11L36.7081 1L40.7081 11L44.7081 1L48.7081 11L52.7081 1L56.7081 11L60.7081 1L64.7081 11M64.8186 11L68.8186 1L72.8186 11L76.8186 1L80.8186 11L84.8186 1L88.8186 11L92.8186 1L96.5982 11L100.598 1L104.598 11L108.598 1L112.598 11L116.598 1L120.598 11L124.598 1L128.598 11"
      />
    </g>

    <foreignObject
      :width="FAHRENHEIT_WIDTH"
      height="80"
    >
      <div class="relative flex h-full flex-col items-center gap-4 pt-4.25">
        <div class="absolute top-4 left-4">
          <slot name="tag" />
        </div>
        <header
          class="text-foreground font-heading text-base leading-6 font-bold tracking-widest uppercase"
        >
          <slot name="title" />
        </header>
        <slot name="badge" />
      </div>
    </foreignObject>

    <!-- Labels and other children are placed in the unit's own coordinates. -->
    <slot />
  </MimicComponent>
</template>
