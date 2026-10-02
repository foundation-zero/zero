<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { LoopCircuitInstance, SeawaterCircuitInstance } from "../../../instances";
import { DC_MIMIC_DATA } from "../data";

const seawaterCircuits = DC_MIMIC_DATA[MimicComponentType.SeawaterCircuit];
const exchangeCircuits = DC_MIMIC_DATA[MimicComponentType.ExchangeCircuit];
</script>

<template>
  <SeawaterCircuitInstance
    x="815.1406"
    y="570.1563"
    force-height
    height="174"
    v-bind="seawaterCircuits.seawater"
  />
  <LoopCircuitInstance
    x="1403"
    y="274.1458"
    force-height
    height="200"
    v-bind="exchangeCircuits.domesticHotWater"
  />
</template>
