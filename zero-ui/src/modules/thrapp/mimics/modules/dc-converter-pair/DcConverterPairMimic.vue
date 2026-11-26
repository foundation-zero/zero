<script setup lang="ts">
import { DcConverterPairFields } from "./dc-converter-pair.types";
import Assets from "./layers/Assets.vue";
import CircuitBoxes from "./layers/CircuitBoxes.vue";
import DirectionArrows from "./layers/DirectionArrows.vue";
import FlowSensors from "./layers/FlowSensors.vue";
import ManualValves from "./layers/ManualValves.vue";
import Pipes from "./layers/Pipes.vue";
import SwitchValves from "./layers/SwitchValves.vue";
import TemperatureSensors from "./layers/TemperatureSensors.vue";

/**
 * The mimic of a group of two DC converters. The groups share one layout (Figma "U-GRID group 2"),
 * so switching between them keeps every pipe, sensor and valve in place.
 */
defineProps<{ fields: DcConverterPairFields }>();
</script>

<template>
  <svg
    viewBox="-20 -15 1146 461"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <DirectionArrows />
    <Pipes />
    <SwitchValves :fields="fields.switchValves" />
    <ManualValves :fields="fields.manualValves" />
    <TemperatureSensors :fields="fields.temperatureSensors" />
    <FlowSensors :fields="fields.flowSensors" />
    <Assets :fields="fields.converters" />
    <CircuitBoxes :field="fields.circuit" />
  </svg>
</template>
