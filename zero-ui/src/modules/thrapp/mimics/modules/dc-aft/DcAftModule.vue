<script setup lang="ts">
import { DcConverterPairFields } from "../dc-converter-pair";
import PairAssets from "../dc-converter-pair/layers/Assets.vue";
import PairCircuitBoxes from "../dc-converter-pair/layers/CircuitBoxes.vue";
import PairDirectionArrows from "../dc-converter-pair/layers/DirectionArrows.vue";
import PairFlowSensors from "../dc-converter-pair/layers/FlowSensors.vue";
import PairManualValves from "../dc-converter-pair/layers/ManualValves.vue";
import PairPipes from "../dc-converter-pair/layers/Pipes.vue";
import PairSwitchValves from "../dc-converter-pair/layers/SwitchValves.vue";
import PairTemperatureSensors from "../dc-converter-pair/layers/TemperatureSensors.vue";
import Assets from "./layers/Assets.vue";
import DirectionArrows from "./layers/DirectionArrows.vue";
import FlowSensors from "./layers/FlowSensors.vue";
import ManualValves from "./layers/ManualValves.vue";
import Pipes from "./layers/Pipes.vue";
import SwitchValves from "./layers/SwitchValves.vue";
import TemperatureSensors from "./layers/TemperatureSensors.vue";

// DC/DC group 1: Brightloops AFT 4 and 3 are drawn as a converter pair, the same as the other
// groups, so switching between them keeps the top half in place. The layers of this module add
// Brightloops AFT 2 and 1 below it, joined to the pair's supply and return.
const UPPER_PAIR: DcConverterPairFields = {
  converters: ["dc:aft-4", "dc:aft-3"],
  circuit: "dc:aft",
  switchValves: ["1068-01", "1068-02"],
  manualValves: ["1167-04", "1167-03"],
  temperatureSensors: ["1038-05", "1038-06"],
  flowSensors: ["1057-04", "1057-05"],
};
</script>

<template>
  <svg
    viewBox="-20 -15 1146 858"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <PairDirectionArrows />
    <DirectionArrows />
    <PairPipes />
    <Pipes />
    <PairSwitchValves :fields="UPPER_PAIR.switchValves" />
    <SwitchValves />
    <PairManualValves :fields="UPPER_PAIR.manualValves" />
    <ManualValves />
    <PairTemperatureSensors :fields="UPPER_PAIR.temperatureSensors" />
    <TemperatureSensors />
    <PairFlowSensors :fields="UPPER_PAIR.flowSensors" />
    <FlowSensors />
    <PairAssets :fields="UPPER_PAIR.converters" />
    <Assets />
    <PairCircuitBoxes :field="UPPER_PAIR.circuit" />
  </svg>
</template>
