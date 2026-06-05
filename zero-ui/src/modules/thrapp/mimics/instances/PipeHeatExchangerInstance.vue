<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import { PipeHeatExchangerState } from "../components/pipe-heat-exchanger";
import PipeHeatExchanger from "../components/pipe-heat-exchanger/PipeHeatExchanger.vue";
import { useRandomizedState } from "../providers/mock-helpers.ts";

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
    :pump-state="state"
  />
</template>
