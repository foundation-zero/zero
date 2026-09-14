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
    y="300"
    force-height
    height="224"
    v-bind="circuits.pvt"
    :tooltip="{ ...circuits.pvt.tooltip, title: 'PVT' }"
  >
    <template #fromIcon>
      <RiArrowUpLine class="text-muted-foreground size-3" />
    </template>
    <template #toIcon>
      <RiArrowUpLine class="text-muted-foreground size-3" />
    </template>
  </ConnectingCircuitInstance>
  <ConnectingCircuitInstance
    x="112"
    y="300"
    force-height
    height="224"
    v-bind="circuits.thrusters"
    :tooltip="{ ...circuits.thrusters.tooltip, title: 'Thrusters' }"
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
    height="224"
    v-bind="circuits.freshwater"
    :tooltip="circuits.freshwater.tooltip"
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
    v-bind="exchangeCircuits.highTempLoop"
    :tooltip="{ ...exchangeCircuits.highTempLoop.tooltip, title: 'Domestic hot water' }"
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
