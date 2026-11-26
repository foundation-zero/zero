<script setup lang="ts">
import { MimicWithMiniMap } from "../../components/mini-map";
import CircuitBoxes from "./layers/CircuitBoxes.vue";
import DirectionArrows from "./layers/DirectionArrows.vue";
import FlowSensors from "./layers/FlowSensors.vue";
import Labels from "./layers/Labels.vue";
import ManualValves from "./layers/ManualValves.vue";
import MiniMap from "./layers/MiniMap.vue";
import Pipes from "./layers/Pipes.vue";
import PvtStrings from "./layers/PvtStrings.vue";
import TemperatureSensors from "./layers/TemperatureSensors.vue";
</script>

<template>
  <!-- The mini map scales with the diagram and moves above it on a portrait screen. -->
  <MimicWithMiniMap
    :diagram="{ x: -20, y: 0, width: 1087, height: 599 }"
    :map="{ x: 0, y: 0, width: 302, height: 445 }"
    :map-height="445"
    :gap="20"
  >
    <template #map>
      <MiniMap />
    </template>
    <DirectionArrows />
    <Pipes />
    <PvtStrings />
    <ManualValves />
    <TemperatureSensors />
    <FlowSensors />
    <Labels />
    <CircuitBoxes />
  </MimicWithMiniMap>
</template>
