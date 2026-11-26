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

// DC/DC group 2: Brightloops FWD 2 and 1. Drawn with the converter pair's layers, like the other DC groups,
// so switching between them keeps every pipe, sensor and valve in place.
const FIELDS: DcConverterPairFields = {
  converters: ["dc:fwd-2", "dc:fwd-1"],
  circuit: "dc:fwd",
  switchValves: ["1068-05", "1068-06"],
  manualValves: ["1167-05", "1167-06"],
  temperatureSensors: ["1038-12", "1038-13"],
  flowSensors: ["1057-11", "1057-12"],
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
