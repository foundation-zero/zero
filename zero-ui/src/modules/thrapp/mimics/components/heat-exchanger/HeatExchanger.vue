<script setup lang="ts">
import { computed, toRefs } from "vue";
import { createSizeAndViewbox, useOrientation } from "..";
import {
  HEAT_EXCHANGER_BASE_ORIENTATION,
  HEAT_EXCHANGER_HEIGHT,
  HEAT_EXCHANGER_SHELL,
  HEAT_EXCHANGER_STATE_COLORS,
  HEAT_EXCHANGER_WIDTH,
  HeatExchangerProps,
  HeatExchangerState,
} from "./index";

const props = withDefaults(defineProps<HeatExchangerProps>(), {
  state: HeatExchangerState.Idle,
  orientation: HEAT_EXCHANGER_BASE_ORIENTATION,
});

const { state, orientation } = toRefs(props);

const colors = computed(() => HEAT_EXCHANGER_STATE_COLORS[state.value]);
const rotation = useOrientation(orientation, HEAT_EXCHANGER_BASE_ORIENTATION);
</script>

<template>
  <svg
    data-slot="heat-exchanger"
    v-bind="createSizeAndViewbox(HEAT_EXCHANGER_WIDTH, HEAT_EXCHANGER_HEIGHT)"
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    aria-hidden="true"
  >
    <g
      :style="rotation"
      class="origin-center transition-transform duration-300"
    >
      <rect
        :x="HEAT_EXCHANGER_SHELL.x"
        :y="HEAT_EXCHANGER_SHELL.y"
        :width="HEAT_EXCHANGER_SHELL.width"
        :height="HEAT_EXCHANGER_SHELL.height"
        :stroke="colors.shell"
        class="transition-colors duration-300"
      />
      <path
        d="M6 10H17L12 12L17 14L12 16L17 18L12 20L17 22L12 24L17 26H6"
        :stroke="colors.exchangerLeft"
        stroke-linejoin="round"
        class="transition-colors duration-300"
      />
      <path
        d="M30 26L19 26L24 24L19 22L24 20L19 18L24 16L19 14L24 12L19 10L30 10"
        :stroke="colors.exchangerRight"
        stroke-linejoin="round"
        class="transition-colors duration-300"
      />
    </g>
  </svg>
</template>
