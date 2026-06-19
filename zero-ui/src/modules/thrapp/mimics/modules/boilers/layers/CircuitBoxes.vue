<script setup lang="ts">
/**
 * Circuit Boxes Layer
 *
 * Displays circuit information boxes for High Temp Loop, Brightloop, Drives, and Fahrenheit.
 * Uses the LoopCircuitInstance component to render each box with real-time temperature and flow data.
 *
 * FIGMA_URL: https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=7149:66096
 */

import { MimicComponentType } from "@/modules/thrapp/types";
import HotWaterCircuitInstance from "../../../instances/HotWaterCircuitInstance.vue";
import { LoopCircuitInstance } from "../../../instances/index.ts";
import { BOILERS_MIMIC_DATA } from "../data";

const circuits = BOILERS_MIMIC_DATA[MimicComponentType.ExchangeCircuit];
const hotWaterCircuits = BOILERS_MIMIC_DATA[MimicComponentType.HotWaterCircuit];
</script>

<template>
  <g>
    <LoopCircuitInstance
      x="0"
      y="25"
      force-height
      v-bind="circuits['highTempLoop']"
    />
    <LoopCircuitInstance
      x="397"
      y="728"
      force-height
      v-bind="circuits['brightloop']"
    />
    <LoopCircuitInstance
      x="650"
      y="728"
      force-height
      v-bind="circuits['drives']"
    />
    <LoopCircuitInstance
      x="903"
      y="728"
      force-height
      v-bind="circuits['fahrenheit']"
    />
    <HotWaterCircuitInstance
      x="1215"
      y="455"
      force-height
      height="300"
      v-bind="hotWaterCircuits['domestic']"
    />
  </g>
</template>
