<script setup lang="ts">
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
    viewBox="-20 0 1087 599"
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
    <Labels />
    <CircuitBoxes />
  </svg>
</template>
