<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ExchangeCircuitInstance, SeawaterCircuitInstance } from "../../../instances";
import { DC_MIMIC_DATA } from "../data";

const seawaterCircuits = DC_MIMIC_DATA[MimicComponentType.SeawaterCircuit];
const exchangeCircuits = DC_MIMIC_DATA[MimicComponentType.ExchangeCircuit];
</script>

<template>
  <SeawaterCircuitInstance
    x="815.1406"
    y="570.1563"
    height="95"
    v-bind="seawaterCircuits.seawater"
  />
  <ExchangeCircuitInstance
    x="1403"
    y="274.1458"
    height="183"
    v-bind="exchangeCircuits.domesticHotWater"
  />
</template>
