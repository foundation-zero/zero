<script setup lang="ts">
import { useMediaQuery } from "@vueuse/core";
import { computed } from "vue";
import { MimicWithMiniMapProps, ViewBox } from "./mini-map.types";
import { getMiniMapLayout } from "./mini-map.utils";

/**
 * A mimic with a mini map of the installation beside it, or above it on a portrait screen. Both are
 * drawn in one SVG, so the mini map scales and zooms together with the diagram.
 */
const props = defineProps<MimicWithMiniMapProps>();

const portrait = useMediaQuery("(orientation: portrait)");

const toViewBox = ({ x, y, width, height }: ViewBox) => `${x} ${y} ${width} ${height}`;

const layout = computed(() => getMiniMapLayout(props, portrait.value));
</script>

<template>
  <svg
    :viewBox="`0 0 ${layout.width} ${layout.height}`"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <svg
      v-bind="layout.map"
      :viewBox="toViewBox(map)"
      overflow="visible"
      data-slot="mini-map"
    >
      <slot name="map" />
    </svg>
    <svg
      v-bind="layout.diagram"
      :viewBox="toViewBox(diagram)"
      overflow="visible"
    >
      <slot />
    </svg>
  </svg>
</template>
