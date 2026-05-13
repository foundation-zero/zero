<script setup lang="ts">
import { computed } from "vue";
import { MimicComponentInstanceProps, useRandomizedState } from ".";
import { HeatingState } from "../components";
import { HeatExchangerPortOrientation } from "../components/heat-exchanger";

import HeatExchanger from "../components/heat-exchanger/HeatExchanger.vue";
import HeatExchangerPort from "../components/heat-exchanger/HeatExchangerPort.vue";

export type HeatExchangerInstanceProps = {
  sideA?: HeatExchangerPortOrientation;
  sideB?: HeatExchangerPortOrientation;
};

const props = withDefaults(
  defineProps<MimicComponentInstanceProps & HeatExchangerInstanceProps>(),
  {
    sideA: HeatExchangerPortOrientation.Side,
    sideB: HeatExchangerPortOrientation.Side,
  },
);

const states: HeatingState[] = [
  HeatingState.CoolingHigh,
  HeatingState.CoolingMedium,
  HeatingState.HeatingHigh,
  HeatingState.HeatingMedium,
  HeatingState.Idle,
];

const stateA = useRandomizedState(states);
const stateB = useRandomizedState(states);

const exchangerState = computed(() => {
  if (stateA.value === HeatingState.Idle && stateB.value === HeatingState.Idle) {
    return HeatingState.Inactive;
  } else {
    return HeatingState.Active;
  }
});
</script>

<template>
  <HeatExchanger
    v-bind="props"
    :state="exchangerState"
  >
    <HeatExchangerPort
      side="a"
      :state="stateA"
      :orientation="sideA"
    />
    <HeatExchangerPort
      side="b"
      :state="stateB"
      :orientation="sideB"
    />
  </HeatExchanger>
</template>
