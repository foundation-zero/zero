<script setup lang="ts">
import { useMediaQuery } from "@vueuse/core";
import { computed } from "vue";
import { MimicWithMiniMapProps, ViewBox } from "./mini-map.types";

/**
 * A mimic with a mini map of the installation beside it, or above it on a portrait screen. Both are
 * drawn in one SVG, so the mini map scales and zooms together with the diagram.
 */
const props = withDefaults(defineProps<MimicWithMiniMapProps>(), { gap: 40 });

const portrait = useMediaQuery("(orientation: portrait)");

const toViewBox = ({ x, y, width, height }: ViewBox) => `${x} ${y} ${width} ${height}`;

const layout = computed(() => {
  const map = {
    width: (props.mapHeight * props.map.width) / props.map.height,
    height: props.mapHeight,
  };
  const diagram = { width: props.diagram.width, height: props.diagram.height };

  if (portrait.value) {
    const width = Math.max(map.width, diagram.width);
    return {
      width,
      height: map.height + props.gap + diagram.height,
      map: { ...map, x: (width - map.width) / 2, y: 0 },
      diagram: { ...diagram, x: (width - diagram.width) / 2, y: map.height + props.gap },
    };
  }

  const height = Math.max(map.height, diagram.height);
  return {
    width: map.width + props.gap + diagram.width,
    height,
    map: { ...map, x: 0, y: (height - map.height) / 2 },
    diagram: { ...diagram, x: map.width + props.gap, y: (height - diagram.height) / 2 },
  };
});
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
