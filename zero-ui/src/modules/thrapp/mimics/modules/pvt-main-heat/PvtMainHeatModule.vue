<script setup lang="ts">
import Outline from "./layers/Outline.vue";
import PanelStrings from "./layers/PanelStrings.vue";
import Pyranometers from "./layers/Pyranometers.vue";
</script>

<template>
  <svg
    viewBox="-10 -15 307 467"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <Outline />
    <PanelStrings />
    <Pyranometers />
  </svg>
</template>
