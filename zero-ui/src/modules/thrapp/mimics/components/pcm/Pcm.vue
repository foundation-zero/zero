<script setup lang="ts">
import { computed, provide } from "vue";
import {
  HEAT_PIPES_BOTTOM_LEFT_POSITION,
  HEAT_PIPES_BOTTOM_RIGHT_POSITION,
  HEAT_PIPES_TOP_LEFT_POSITION,
  PCM_CONTENT_RIGHT_DIAGONAL,
  PCM_CONTENT_RIGHT_WITH_PORTS,
  PCM_HEIGHT,
  PCM_WIDTH,
  PcmLayout,
  PcmProps,
} from ".";
import { MimicComponentBaseProps } from "..";
import MimicComponent from "../MimicComponent.vue";
import HeatPipe from "./HeatPipe.vue";

const props = withDefaults(defineProps<PcmProps & MimicComponentBaseProps>(), {
  layout: () => PcmLayout.LeftTopBottom,
});

const contentRightPadding = computed(() =>
  props.layout === PcmLayout.LeftRight ? PCM_CONTENT_RIGHT_DIAGONAL : PCM_CONTENT_RIGHT_WITH_PORTS,
);

provide("contentRightPadding", contentRightPadding);
</script>

<template>
  <MimicComponent
    v-slot="{ stateColor, strokeWidth }"
    :width="PCM_WIDTH"
    :height="PCM_HEIGHT"
    v-bind="props"
    :class="layout"
  >
    <rect
      x="0.5"
      y="0.5"
      :width="PCM_WIDTH - 1"
      :height="PCM_HEIGHT - 1"
      class="fill-background"
      :stroke="stateColor"
      :stroke-width="strokeWidth"
    />
    <HeatPipe v-bind="HEAT_PIPES_TOP_LEFT_POSITION" />
    <HeatPipe
      v-if="layout === PcmLayout.LeftTopBottom"
      v-bind="HEAT_PIPES_BOTTOM_LEFT_POSITION"
    />
    <HeatPipe
      v-else-if="layout === PcmLayout.LeftRight"
      v-bind="HEAT_PIPES_BOTTOM_RIGHT_POSITION"
      orientation="right"
    />
    <g
      class="fill-foreground text-[12px]"
      font-family="Inter"
    >
      <g v-if="layout === PcmLayout.LeftTopBottom">
        <text
          x="9"
          y="28"
          >B</text
        >
        <text
          x="9"
          y="88"
          >A</text
        >
        <text
          x="9"
          y="115"
          >D</text
        >
        <text
          x="9"
          y="173"
          >C</text
        >
      </g>
      <g v-else>
        <text
          x="9"
          y="28"
          >B</text
        >
        <text
          x="9"
          y="88"
          >C</text
        >
        <text
          :x="PCM_WIDTH - 16"
          y="115"
          >A</text
        >
        <text
          :x="PCM_WIDTH - 16"
          y="173"
          >D</text
        >
      </g>
    </g>
    <foreignObject
      :width="PCM_WIDTH"
      :height="PCM_HEIGHT"
    >
      <div class="flex flex-col gap-1 px-4 pt-0.5 pl-12.5">
        <slot />
      </div>
    </foreignObject>
  </MimicComponent>
</template>
