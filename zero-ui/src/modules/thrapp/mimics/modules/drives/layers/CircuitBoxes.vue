<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { LoopCircuitInstance, SeawaterCircuitInstance } from "../../../instances";
import { DRIVES_EXCHANGE_CIRCUIT_DATA } from "../data";

const seawaterCircuits = DRIVES_EXCHANGE_CIRCUIT_DATA[MimicComponentType.SeawaterCircuit];
const exchangeCircuits = DRIVES_EXCHANGE_CIRCUIT_DATA[MimicComponentType.ExchangeCircuit];
</script>

<template>
  <SeawaterCircuitInstance
    x="1039.2832"
    y="782.916"
    :width="196"
    :height="76"
    force-height
    v-bind="seawaterCircuits.seawater"
  />
  <LoopCircuitInstance
    x="1314"
    y="19.916"
    :width="196"
    :height="220"
    force-height
    v-bind="exchangeCircuits.domesticHotWater"
  />
</template>
