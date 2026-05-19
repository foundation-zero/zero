<script setup lang="ts">
/**
 * Circuit Boxes Layer
 *
 * Displays circuit information boxes for High Temp Loop, Brightloop, Drives, and Fahrenheit.
 * Uses the LoopCircuitInstance component to render each box with real-time temperature and flow data.
 *
 * FIGMA_URL: https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=7149:66096
 */

import { LoopCircuitInstance } from "../../../instances";
</script>

<template>
  <g>
    <LoopCircuitInstance
      x="0"
      y="25"
      title="High Temp Loop"
    />
    <LoopCircuitInstance
      x="397"
      y="730"
      title="Brightloop"
    />
    <LoopCircuitInstance
      x="650"
      y="730"
      title="Drives"
    />
    <LoopCircuitInstance
      x="903"
      y="730"
      title="Fahrenheit"
    />
  </g>
</template>
