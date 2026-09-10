<script setup lang="ts">
import { Ratio } from "@/modules/thrsim/types/index.ts";
import { computed } from "vue";
import {
  createThreeWayValveFlows,
  createValveLegLabel,
  THREE_WAY_VALVE_DEFAULT_LEGS,
  ThreeWayValveLegs,
  VALVE_LEGS,
  ValveLeg,
} from "./index.ts";
import ValveLegLabel from "./ValveLegLabel.vue";
import ValvePortBottom from "./ValvePortBottom.vue";
import ValvePortLeft from "./ValvePortLeft.vue";
import ValvePortRight from "./ValvePortRight.vue";

const props = withDefaults(defineProps<{ flow: Ratio; legs?: ThreeWayValveLegs }>(), {
  legs: () => THREE_WAY_VALVE_DEFAULT_LEGS,
});

const flows = computed(() => createThreeWayValveFlows(props.legs, props.flow));

const labels = computed(() =>
  VALVE_LEGS.map((leg) => ({
    leg,
    port: props.legs[leg],
    anchor: createValveLegLabel(leg, props.legs[leg]),
  })),
);
</script>

<template>
  <ValvePortLeft :flow="flows[ValveLeg.Left]" />
  <ValvePortRight :flow="flows[ValveLeg.Right]" />
  <ValvePortBottom :flow="flows[ValveLeg.Bottom]" />

  <ValveLegLabel
    v-for="{ leg, port, anchor } in labels"
    :key="leg"
    v-bind="anchor"
  >
    {{ port }}
  </ValveLegLabel>
</template>
