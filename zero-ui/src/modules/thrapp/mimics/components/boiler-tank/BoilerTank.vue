<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { computed, HTMLAttributes } from "vue";
import {
  BOILER_TANK_HEIGHT,
  BOILER_TANK_LEVEL_LINE_OFFSET,
  BOILER_TANK_MODE_COLORS,
  BOILER_TANK_WIDTH,
  BoilerTankModes,
} from ".";
import { createSizeAndViewbox } from "..";
import BoilerTankLevel from "./BoilerTankLevel.vue";
import BoilerTankLevelIndicator from "./BoilerTankLevelIndicator.vue";

const props = defineProps<{
  class?: HTMLAttributes["class"];
  level: number;
  mode: BoilerTankModes;
}>();

const color = computed(() => BOILER_TANK_MODE_COLORS[props.mode]);
</script>

<template>
  <svg
    v-bind="createSizeAndViewbox(BOILER_TANK_WIDTH, BOILER_TANK_HEIGHT)"
    class="fill-background"
  >
    <g mask="url(#boiler-tank-mask)">
      <rect
        :width="BOILER_TANK_WIDTH"
        :height="BOILER_TANK_HEIGHT"
        class="fill-background"
      />

      <g
        class="transition-all"
        :style="{
          transform: `translateY(${100 - Math.min(100, level)}%)`,
        }"
      >
        <BoilerTankLevel :y="-BOILER_TANK_LEVEL_LINE_OFFSET" />
      </g>

      <BoilerTankLevelIndicator
        x="1"
        y="0"
      />
    </g>
    <defs>
      <mask id="boiler-tank-mask">
        <rect
          :width="BOILER_TANK_WIDTH - 2"
          :height="BOILER_TANK_HEIGHT - 2"
          x="1"
          y="1"
          rx="8"
          ry="8"
          fill="white"
        />
      </mask>
    </defs>
    <foreignObject
      width="100%"
      height="100%"
    >
      <div
        :class="cn('h-37 w-51 rounded-md border pr-2 pb-1 pl-3 transition-colors', props.class)"
        :style="{ borderColor: color }"
      >
        <slot />
      </div>
    </foreignObject>
  </svg>
</template>
