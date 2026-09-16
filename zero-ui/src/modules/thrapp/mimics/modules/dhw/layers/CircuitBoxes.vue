<script setup lang="ts">
/**
 * Circuit Boxes Layer
 *
 * Displays circuit information boxes for High Temp Loop, DC Converters, Drives, and Adsorption.
 * Uses the LoopCircuitInstance component to render each box with real-time temperature and flow data.
 *
 * FIGMA_URL: https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=7149:66096
 */

import { MimicComponentType } from "@/modules/thrapp/types";
import ConnectingCircuitInstance from "../../../instances/ConnectingCircuitInstance.vue";
import { ExchangeCircuitInstance } from "../../../instances/index.ts";
import { DHW_MIMIC_DATA } from "../data/index.ts";

const circuits = DHW_MIMIC_DATA[MimicComponentType.ExchangeCircuit];
const connectingCircuits = DHW_MIMIC_DATA[MimicComponentType.ConnectingCircuit];
</script>

<template>
  <g>
    <ExchangeCircuitInstance
      x="0"
      y="0"
      v-bind="circuits['highTempLoop']"
    />
    <ExchangeCircuitInstance
      x="397"
      y="708"
      v-bind="circuits['dcConverters']"
    />
    <ExchangeCircuitInstance
      x="650"
      y="708"
      v-bind="circuits['drives']"
    />
    <ExchangeCircuitInstance
      x="903"
      y="708"
      v-bind="circuits['adsorption']"
    />
    <ConnectingCircuitInstance
      x="1215"
      y="455"
      v-bind="connectingCircuits['freshwater']"
    />
  </g>
</template>
