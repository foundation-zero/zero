<script setup lang="ts">
import ActuatedValves from "./layers/ActuatedValves.vue";
import CircuitBoxes from "./layers/CircuitBoxes.vue";
import DirectionArrows from "./layers/DirectionArrows.vue";
import ExpansionTanks from "./layers/ExpansionTanks.vue";
import FlowSensors from "./layers/FlowSensors.vue";
import HeatExchangers from "./layers/HeatExchangers.vue";
import ManualValves from "./layers/ManualValves.vue";
import Pipes from "./layers/Pipes.vue";
import PressureGauges from "./layers/PressureGauges.vue";
import TemperatureSensors from "./layers/TemperatureSensors.vue";
</script>

<template>
  <!-- The Fahrenheit chiller asset is not part of the mimic yet. -->
  <svg
    viewBox="0 0 1848 677"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <Pipes />
    <DirectionArrows />
    <HeatExchangers />
    <ActuatedValves />
    <ManualValves />
    <ExpansionTanks />
    <PressureGauges />
    <FlowSensors />
    <TemperatureSensors />
    <CircuitBoxes />
  </svg>
</template>
