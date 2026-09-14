<script setup lang="ts">
import AirTrapVessels from "./layers/AirTrapVessels.vue";
import CheckValves from "./layers/CheckValves.vue";
import CircuitBoxes from "./layers/CircuitBoxes.vue";
import ConnectingCircuits from "./layers/ConnectingCircuits.vue";
import DirectionArrows from "./layers/DirectionArrows.vue";
import FlowControlValves from "./layers/FlowControlValves.vue";
import FlowSensors from "./layers/FlowSensors.vue";
import HeatBatteries from "./layers/HeatBatteries.vue";
import HeatExchangers from "./layers/HeatExchangers.vue";
import ManualValves from "./layers/ManualValves.vue";
import Pipes from "./layers/Pipes.vue";
import PressureGauges from "./layers/PressureGauges.vue";
import Pumps from "./layers/Pumps.vue";
import SwitchValves from "./layers/SwitchValves.vue";
import TemperatureSensors from "./layers/TemperatureSensors.vue";
</script>

<template>
  <svg
    width="1750"
    height="935"
    viewBox="-100 -25 1700 890"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <Pipes />
    <DirectionArrows
      x="115"
      y="7"
    />
    <ConnectingCircuits
      x="968"
      y="127"
    />
    <CircuitBoxes />
    <HeatBatteries />
    <HeatExchangers />
    <FlowSensors />
    <FlowControlValves />
    <SwitchValves />
    <TemperatureSensors />
    <ManualValves />
    <CheckValves />
    <PressureGauges />
    <AirTrapVessels />
    <Pumps />
  </svg>
</template>
