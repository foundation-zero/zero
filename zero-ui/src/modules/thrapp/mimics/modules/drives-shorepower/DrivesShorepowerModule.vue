<script setup lang="ts">
import Assets from "./layers/Assets.vue";
import CircuitBoxes from "./layers/CircuitBoxes.vue";
import ConverterValves from "./layers/ConverterValves.vue";
import DirectionArrows from "./layers/DirectionArrows.vue";
import ManualValves from "./layers/ManualValves.vue";
import Pipes from "./layers/Pipes.vue";
import Sections from "./layers/Sections.vue";
</script>

<template>
  <svg
    viewBox="0 0 1135 851"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <Sections />
    <DirectionArrows />
    <Pipes />
    <ConverterValves />
    <ManualValves />
    <Assets />
    <CircuitBoxes />
  </svg>
</template>
