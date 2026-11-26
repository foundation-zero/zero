<script setup lang="ts">
import { MimicWithMiniMap } from "../../components/mini-map";
import Assets from "./layers/Assets.vue";
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
    :diagram="{ x: -20, y: -20, width: 1630, height: 692 }"
    :map="{ x: -1, y: -1, width: 287, height: 427 }"
    :map-height="531"
    :gap="30"
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
    <Assets />
    <Labels />
    <CircuitBoxes />
  </MimicWithMiniMap>
</template>
