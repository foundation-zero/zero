<script setup lang="ts">
import { MimicComponentInstanceProps, useRandomizedState } from ".";
import { PipeHeatExchangerState } from "../components/pipe-heat-exchanger";
import PipeHeatExchanger from "../components/pipe-heat-exchanger/PipeHeatExchanger.vue";

const props = defineProps<MimicComponentInstanceProps>();

const state = useRandomizedState([
  PipeHeatExchangerState.Cooling,
  PipeHeatExchangerState.Heating,
  PipeHeatExchangerState.Idle,
]);
</script>

<template>
  <PipeHeatExchanger
    v-bind="props"
    :state="state"
  />
</template>
