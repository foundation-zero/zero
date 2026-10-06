<script setup lang="ts">
import Assets from "./layers/Assets.vue";
import CheckValves from "./layers/CheckValves.vue";
import CircuitBoxes from "./layers/CircuitBoxes.vue";
import DirectionArrows from "./layers/DirectionArrows.vue";
import ExpansionTanks from "./layers/ExpansionTanks.vue";
import FlowControlValves from "./layers/FlowControlValves.vue";
import FlowSensors from "./layers/FlowSensors.vue";
import HeatExchangers from "./layers/HeatExchangers.vue";
import ManualValves from "./layers/ManualValves.vue";
import MixValves from "./layers/MixValves.vue";
import Pipes from "./layers/Pipes.vue";
import PressureGauges from "./layers/PressureGauges.vue";
import PressureSensors from "./layers/PressureSensors.vue";
import Pumps from "./layers/Pumps.vue";
import SwitchValves from "./layers/SwitchValves.vue";
import TemperatureSensors from "./layers/TemperatureSensors.vue";
</script>

<template>
  <svg
    viewBox="0 0 1718 890"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <Pipes />
    <ExpansionTanks />
    <HeatExchangers />
    <MixValves />
    <ManualValves />
    <CheckValves />
    <SwitchValves />
    <FlowControlValves />
    <Pumps />
    <FlowSensors />
    <PressureSensors />
    <PressureGauges />
    <TemperatureSensors />
    <DirectionArrows
      x="395"
      y="92"
    />
    <Assets />
    <CircuitBoxes />
  </svg>
</template>
