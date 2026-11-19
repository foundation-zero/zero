<script setup lang="ts">
import Assets from "./layers/Assets.vue";
import CircuitBoxes from "./layers/CircuitBoxes.vue";
import DirectionArrows from "./layers/DirectionArrows.vue";
import FlowSensors from "./layers/FlowSensors.vue";
import ManualValves from "./layers/ManualValves.vue";
import Pipes from "./layers/Pipes.vue";
import SwitchValves from "./layers/SwitchValves.vue";
import TemperatureSensors from "./layers/TemperatureSensors.vue";
</script>

<template>
  <svg
    viewBox="-20 -15 1146 858"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <DirectionArrows />
    <Pipes />
    <SwitchValves />
    <ManualValves />
    <TemperatureSensors />
    <FlowSensors />
    <Assets />
    <CircuitBoxes />
  </svg>
</template>
