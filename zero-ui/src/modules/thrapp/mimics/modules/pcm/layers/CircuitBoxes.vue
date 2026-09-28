<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { RiArrowLeftLine, RiArrowRightLine, RiArrowUpLine } from "@remixicon/vue";
import ConnectingCircuitInstance from "../../../instances/ConnectingCircuitInstance.vue";
import LoopCircuitInstance from "../../../instances/LoopCircuitInstance.vue";
import { PCM_MIMIC_DATA } from "../data";

const circuits = PCM_MIMIC_DATA[MimicComponentType.ConnectingCircuit];
const exchangeCircuits = PCM_MIMIC_DATA[MimicComponentType.ExchangeCircuit];
</script>

<template>
  <ConnectingCircuitInstance
    x="-93"
    y="288"
    force-height
    height="300"
    v-bind="circuits.pvt"
  >
    <template #fromIcon>
      <RiArrowUpLine class="text-muted-foreground size-3" />
    </template>
    <template #toIcon>
      <RiArrowLeftLine class="text-muted-foreground size-3" />
    </template>
  </ConnectingCircuitInstance>
  <ConnectingCircuitInstance
    x="112"
    y="288"
    force-height
    height="250"
    v-bind="circuits.thrusters"
  >
    <template #fromIcon>
      <RiArrowUpLine class="text-muted-foreground size-3" />
    </template>
    <template #toIcon>
      <RiArrowUpLine class="text-muted-foreground size-3" />
    </template>
  </ConnectingCircuitInstance>
  <ConnectingCircuitInstance
    x="1400"
    y="10"
    force-height
    height="230"
    v-bind="circuits.freshwater"
  >
    <template #fromIcon>
      <RiArrowRightLine class="text-muted-foreground size-3" />
    </template>
    <template #toIcon>
      <RiArrowLeftLine class="text-muted-foreground size-3" />
    </template>
  </ConnectingCircuitInstance>
  <LoopCircuitInstance
    x="1400"
    y="262"
    force-height
    height="198"
    v-bind="exchangeCircuits.dhw"
  />
  <LoopCircuitInstance
    x="1400"
    y="440"
    force-height
    height="174"
    v-bind="exchangeCircuits.adsorption"
    :tooltip="exchangeCircuits.adsorption.tooltip"
  />
</template>
