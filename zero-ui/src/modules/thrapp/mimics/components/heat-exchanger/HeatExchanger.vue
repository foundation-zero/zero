<script setup lang="ts">
import { computed, toRefs } from "vue";
import { MimicComponentBaseProps } from "..";
import MimicComponent from "../MimicComponent.vue";
import {
  HEAT_EXCHANGER_BASE_ORIENTATION,
  HEAT_EXCHANGER_HEIGHT,
  HEAT_EXCHANGER_SHELL,
  HEAT_EXCHANGER_STATE_COLORS,
  HEAT_EXCHANGER_WIDTH,
  HeatExchangerProps,
  HeatExchangerState,
} from "./index";

const props = withDefaults(defineProps<HeatExchangerProps & MimicComponentBaseProps>(), {
  state: HeatExchangerState.Idle,
  orientation: HEAT_EXCHANGER_BASE_ORIENTATION,
});

const { state } = toRefs(props);

const colors = computed(() => HEAT_EXCHANGER_STATE_COLORS[state.value]);
</script>

<template>
  <MimicComponent
    :width="HEAT_EXCHANGER_WIDTH"
    :height="HEAT_EXCHANGER_HEIGHT"
    :base-orientation="HEAT_EXCHANGER_BASE_ORIENTATION"
    :orientation="orientation"
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
  </MimicComponent>
</template>
