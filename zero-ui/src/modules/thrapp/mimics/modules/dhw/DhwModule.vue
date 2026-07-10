<script setup lang="ts">
import ActuatedValves from "./layers/ActuatedValves.vue";
import Assets from "./layers/Assets.vue";
import BoilerTanks from "./layers/BoilerTanks.vue";
import Bypasses from "./layers/Bypasses.vue";
import CircuitBoxes from "./layers/CircuitBoxes.vue";
import DirectionArrows from "./layers/DirectionArrows.vue";
import Flows from "./layers/Flows.vue";
import FlowSensors from "./layers/FlowSensors.vue";
import HeatExchangers from "./layers/HeatExchangers.vue";
import Labels from "./layers/Labels.vue";
import LevelSensors from "./layers/LevelSensors.vue";
import ManualValves from "./layers/ManualValves.vue";
import Pipes from "./layers/Pipes.vue";
import PressureGauges from "./layers/PressureGauges.vue";
import PressureSensors from "./layers/PressureSensors.vue";
import Pumps from "./layers/Pumps.vue";
import TemperatureSensors from "./layers/TemperatureSensors.vue";
</script>

<template>
  <svg
    viewBox="0 -10 1414 864"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <Bypasses />
    <Pipes />
    <Flows />
    <HeatExchangers />
    <ActuatedValves />
    <ManualValves />
    <Pumps />
    <LevelSensors />
    <PressureSensors />
    <PressureGauges />
    <FlowSensors />
    <TemperatureSensors />
    <Labels />
    <DirectionArrows />
    <CircuitBoxes />
    <BoilerTanks />
    <Assets />
  </svg>
</template>
