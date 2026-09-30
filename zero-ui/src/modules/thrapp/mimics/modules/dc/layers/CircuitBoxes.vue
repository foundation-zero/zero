<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { LoopCircuitInstance } from "../../../instances";
import { DC_MIMIC_DATA } from "../data";

const circuits = DC_MIMIC_DATA[MimicComponentType.ExchangeCircuit];
</script>

<template>
  <LoopCircuitInstance
    x="815.1406"
    y="590.1563"
    force-height
    v-bind="circuits.seawater"
  />
  <LoopCircuitInstance
    x="1403"
    y="274.1458"
    force-height
    height="174"
    v-bind="circuits.domesticHotWater"
  />
</template>
