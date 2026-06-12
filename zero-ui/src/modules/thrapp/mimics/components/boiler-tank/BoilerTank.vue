<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { BoilerTankState } from "@/modules/thrs/types/index.ts";
import { computed, HTMLAttributes, toRefs } from "vue";
import {
  BOILER_TANK_HEIGHT,
  BOILER_TANK_LEVEL_LINE_OFFSET,
  BOILER_TANK_MODE_COLORS,
  BOILER_TANK_WIDTH,
} from ".";
import {
  createMimicComponentContext,
  createSizeAndViewbox,
  MimicComponentState,
  provideMimicComponentContext,
} from "..";
import BoilerTankLevel from "./BoilerTankLevel.vue";
import BoilerTankLevelIndicator from "./BoilerTankLevelIndicator.vue";

const props = withDefaults(
  defineProps<{
    class?: HTMLAttributes["class"];
    level: number;
    mode?: BoilerTankState;
    width?: number | string;
    height?: number | string;
    forceHeight?: boolean;
    state?: MimicComponentState;
  }>(),
  {
    state: MimicComponentState.Normal,
    width: () => BOILER_TANK_WIDTH,
    height: () => BOILER_TANK_HEIGHT,
    forceHeight: false,
    mode: BoilerTankState.Standby,
  },
);

const { state } = toRefs(props);

const { strokeWidth } = provideMimicComponentContext(createMimicComponentContext(state));

const color = computed(() => {
  if (state.value === MimicComponentState.Normal) {
    return BOILER_TANK_MODE_COLORS[props.mode];
  } else {
    return BOILER_TANK_MODE_COLORS[state.value];
  }
});
</script>

<template>
  <svg
    v-bind="createSizeAndViewbox(width, height, forceHeight)"
    class="fill-background"
  >
    <g mask="url(#boiler-tank-mask)">
      <rect
        :width="width"
        :height="height"
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
          :width="+width - 2"
          :height="+height - 2"
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
        :class="cn('h-37 w-51 rounded-md border transition-all', props.class)"
        :style="{ borderColor: color, borderWidth: `${strokeWidth}px` }"
      />
    </foreignObject>
    <foreignObject
      width="100%"
      height="100%"
    >
      <div :class="cn('h-37 w-51 pr-2 pb-1 pl-3', props.class)">
        <slot />
      </div>
    </foreignObject>
  </svg>
</template>
