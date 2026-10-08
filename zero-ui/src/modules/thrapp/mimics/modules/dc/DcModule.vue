<script setup lang="ts">
import Assets from "./layers/Assets.vue";
import CheckValves from "./layers/CheckValves.vue";
import CircuitBoxes from "./layers/CircuitBoxes.vue";
import DirectionArrows from "./layers/DirectionArrows.vue";
import ExpansionTanks from "./layers/ExpansionTanks.vue";
import FlowSensors from "./layers/FlowSensors.vue";
import HeatExchangers from "./layers/HeatExchangers.vue";
import MixValves from "./layers/MixValves.vue";
import Pipes from "./layers/Pipes.vue";
import PressureGauges from "./layers/PressureGauges.vue";
import PressureSensors from "./layers/PressureSensors.vue";
import Pumps from "./layers/Pumps.vue";
import TemperatureSensors from "./layers/TemperatureSensors.vue";
</script>

<template>
  <!-- viewBox is a placeholder until the Figma frame geometry is captured -->
  <svg
    viewBox="0 0 1610 718"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <Pipes />
    <HeatExchangers />
    <MixValves />
    <CheckValves />
    <Pumps />
    <ExpansionTanks />
    <PressureSensors />
    <PressureGauges />
    <FlowSensors />
    <TemperatureSensors />
    <DirectionArrows
      x="250"
      y="110"
    />
    <CircuitBoxes />
    <Assets />
  </svg>
</template>
