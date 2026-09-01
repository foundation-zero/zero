<script setup lang="ts">
import ActuatedValves from "./layers/ActuatedValves.vue";
import Assets from "./layers/Assets.vue";
import Bypasses from "./layers/Bypasses.vue";
import CheckValves from "./layers/CheckValves.vue";
import CircuitBoxes from "./layers/CircuitBoxes.vue";
import DirectionArrows from "./layers/DirectionArrows.vue";
import ExpansionTanks from "./layers/ExpansionTanks.vue";
import FlowControlValves from "./layers/FlowControlValves.vue";
import FlowSensors from "./layers/FlowSensors.vue";
import HeatExchangers from "./layers/HeatExchangers.vue";
import Labels from "./layers/Labels.vue";
import ManualValves from "./layers/ManualValves.vue";
import Pipes from "./layers/Pipes.vue";
import PressureGauges from "./layers/PressureGauges.vue";
import PressureSensors from "./layers/PressureSensors.vue";
import Pumps from "./layers/Pumps.vue";
import TemperatureSensors from "./layers/TemperatureSensors.vue";
</script>

<template>
  <svg
    viewBox="-60 0 1358 715"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <Bypasses />
    <DirectionArrows />
    <Pipes />
    <HeatExchangers />
    <CheckValves />
    <ActuatedValves />
    <FlowControlValves />
    <ManualValves />
    <Pumps />
    <PressureSensors />
    <PressureGauges />
    <FlowSensors />
    <TemperatureSensors />
    <Labels />
    <CircuitBoxes />
    <Assets />
    <ExpansionTanks />
  </svg>
</template>
