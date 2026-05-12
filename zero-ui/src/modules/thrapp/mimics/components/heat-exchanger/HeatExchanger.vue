<script setup lang="ts">
import { computed } from "vue";
import { HEATING_STATE_COLORS, HeatingState, MimicComponentBaseProps } from "..";
import MimicComponent from "../MimicComponent.vue";
import {
  HEAT_EXCHANGER_BASE_ORIENTATION,
  HEAT_EXCHANGER_HEIGHT,
  HEAT_EXCHANGER_SHELL,
  HEAT_EXCHANGER_WIDTH,
  HeatExchangerProps,
} from "./index";

const props = withDefaults(defineProps<HeatExchangerProps & MimicComponentBaseProps>(), {
  state: HeatingState.Idle,
  orientation: HEAT_EXCHANGER_BASE_ORIENTATION,
});

const shellState = computed(() =>
  props.state === HeatingState.Idle ? HeatingState.Inactive : HeatingState.Active,
);

const shellColor = computed(() => HEATING_STATE_COLORS[shellState.value]);
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
      :stroke="shellColor"
      stroke-width="2"
      class="transition-colors duration-300"
    />
    <slot />
  </MimicComponent>
</template>
