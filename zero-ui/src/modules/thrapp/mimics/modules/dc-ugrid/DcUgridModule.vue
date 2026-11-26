<script setup lang="ts">
import { DcConverterPairFields } from "../dc-converter-pair";
import Assets from "../dc-converter-pair/layers/Assets.vue";
import CircuitBoxes from "../dc-converter-pair/layers/CircuitBoxes.vue";
import DirectionArrows from "../dc-converter-pair/layers/DirectionArrows.vue";
import FlowSensors from "../dc-converter-pair/layers/FlowSensors.vue";
import ManualValves from "../dc-converter-pair/layers/ManualValves.vue";
import Pipes from "../dc-converter-pair/layers/Pipes.vue";
import SwitchValves from "../dc-converter-pair/layers/SwitchValves.vue";
import TemperatureSensors from "../dc-converter-pair/layers/TemperatureSensors.vue";

// DC/AC group 1: U-Grids 2 and 1. Drawn with the converter pair's layers, like the other DC groups,
// so switching between them keeps every pipe, sensor and valve in place.
const FIELDS: DcConverterPairFields = {
  converters: ["dc:ugrid-2", "dc:ugrid-1"],
  circuit: "dc:ugrid",
  switchValves: ["1069-02", "1069-03"],
  manualValves: ["1168-10", "1168-11"],
  temperatureSensors: ["1038-09", "1038-10"],
  flowSensors: ["1057-08", "1057-09"],
};
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
    <SwitchValves :fields="FIELDS.switchValves" />
    <ManualValves :fields="FIELDS.manualValves" />
    <TemperatureSensors :fields="FIELDS.temperatureSensors" />
    <FlowSensors :fields="FIELDS.flowSensors" />
    <Assets :fields="FIELDS.converters" />
    <CircuitBoxes :field="FIELDS.circuit" />
  </svg>
</template>
