<script setup lang="ts">
import ActuatedValves from "./layers/ActuatedValves.vue";
import AirTrapVessels from "./layers/AirTrapVessels.vue";
import Assets from "./layers/Assets.vue";
import BoilerTanks from "./layers/BoilerTanks.vue";
import Bypasses from "./layers/Bypasses.vue";
import CheckValves from "./layers/CheckValves.vue";
import CircuitBoxes from "./layers/CircuitBoxes.vue";
import ConnectingCircuits from "./layers/ConnectingCircuits.vue";
import DirectionArrows from "./layers/DirectionArrows.vue";
import ExpansionTanks from "./layers/ExpansionTanks.vue";
import FlowControlValves from "./layers/FlowControlValves.vue";
import FlowSensors from "./layers/FlowSensors.vue";
import Flows from "./layers/Flows.vue";
import HeatBatteries from "./layers/HeatBatteries.vue";
import HeatExchangers from "./layers/HeatExchangers.vue";
import Labels from "./layers/Labels.vue";
import LevelSensors from "./layers/LevelSensors.vue";
import LevelSwitches from "./layers/LevelSwitches.vue";
import ManualValves from "./layers/ManualValves.vue";
import Pipes from "./layers/Pipes.vue";
import PressureGauges from "./layers/PressureGauges.vue";
import PressureSensors from "./layers/PressureSensors.vue";
import Pumps from "./layers/Pumps.vue";
import SwitchValves from "./layers/SwitchValves.vue";
import TemperatureSensors from "./layers/TemperatureSensors.vue";
</script>

<template>
  <!-- viewBox is a placeholder until the Figma frame geometry is captured -->
  <svg
    viewBox="0 0 1599 718"
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
    <CheckValves />
    <SwitchValves />
    <FlowControlValves />
    <Pumps />
    <ConnectingCircuits />
    <ExpansionTanks />
    <AirTrapVessels />
    <BoilerTanks />
    <HeatBatteries />
    <LevelSensors />
    <LevelSwitches />
    <PressureSensors />
    <PressureGauges />
    <FlowSensors />
    <TemperatureSensors />
    <Labels />
    <DirectionArrows
      x="250"
      y="110"
    />
    <CircuitBoxes />
    <Assets />
  </svg>
</template>
