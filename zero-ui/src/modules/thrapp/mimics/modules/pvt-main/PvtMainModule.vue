<script setup lang="ts">
import Assets from "./layers/Assets.vue";
import CircuitBoxes from "./layers/CircuitBoxes.vue";
import DirectionArrows from "./layers/DirectionArrows.vue";
import FlowSensors from "./layers/FlowSensors.vue";
import Labels from "./layers/Labels.vue";
import ManualValves from "./layers/ManualValves.vue";
import Pipes from "./layers/Pipes.vue";
import PvtStrings from "./layers/PvtStrings.vue";
import TemperatureSensors from "./layers/TemperatureSensors.vue";
</script>

<template>
  <svg
    viewBox="0 0 1600 652"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <DirectionArrows />
    <Pipes />
    <PvtStrings />
    <ManualValves />
    <TemperatureSensors />
    <FlowSensors />
    <Assets />
    <Labels />
    <CircuitBoxes />
  </svg>
</template>
