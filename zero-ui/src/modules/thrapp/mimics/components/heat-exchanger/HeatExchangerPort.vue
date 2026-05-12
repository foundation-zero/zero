<script setup lang="ts">
import { computed } from "vue";
import {
  HEAT_EXCHANGER_HEIGHT,
  HEAT_EXCHANGER_PORT_CONNECTOR_R,
  HEAT_EXCHANGER_PORT_CONNECTORS,
  HEAT_EXCHANGER_PORT_PATHS,
  HEAT_EXCHANGER_WIDTH,
  HeatExchangerPortProps,
} from ".";
import { ComponentOrientation, HEATING_STATE_COLORS, HeatingState } from "..";
import MimicComponent from "../MimicComponent.vue";

const props = defineProps<HeatExchangerPortProps>();

const connectors = computed(() => HEAT_EXCHANGER_PORT_CONNECTORS[props.orientation]);
const path = computed(() => HEAT_EXCHANGER_PORT_PATHS[props.orientation]);
const stateColor = computed(() => HEATING_STATE_COLORS[props.state]);
const connectorState = computed(() =>
  props.state === HeatingState.Idle ? HeatingState.Inactive : HeatingState.Active,
);
const connectorColor = computed(() => HEATING_STATE_COLORS[connectorState.value]);
const flipOrientation = computed(() =>
  props.side === "b" ? ComponentOrientation.Right : ComponentOrientation.Left,
);
</script>

<template>
  <MimicComponent
    :width="HEAT_EXCHANGER_WIDTH"
    :height="HEAT_EXCHANGER_HEIGHT"
    :base-orientation="ComponentOrientation.Left"
    :orientation="flipOrientation"
  >
    <circle
      v-for="(pt, i) in connectors"
      :key="`port-${i}`"
      :cx="pt.cx"
      :cy="pt.cy"
      :r="HEAT_EXCHANGER_PORT_CONNECTOR_R"
      :stroke="connectorColor"
      stroke-width="2"
      fill="var(--background)"
    />

    <path
      :d="path"
      :stroke="stateColor"
      stroke-width="2"
      stroke-linejoin="round"
      class="transition-colors duration-300"
    />
  </MimicComponent>
</template>
