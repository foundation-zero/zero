<script setup lang="ts">
import { toRefs } from "vue";
import { ComponentOrientation, createSizeAndViewbox, MimicComponentProps, useOrientation } from ".";

const props = withDefaults(defineProps<MimicComponentProps>(), {
  orientation: ComponentOrientation.Up,
  baseOrientation: ComponentOrientation.Up,
});

const { baseOrientation, orientation } = toRefs(props);

const rotationStyle = useOrientation(orientation, baseOrientation);
</script>

<template>
  <svg
    v-bind="createSizeAndViewbox(width, height)"
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    aria-hidden="true"
  >
    <g
      :style="rotationStyle"
      class="origin-center transition-transform duration-300"
    >
      <slot />
    </g>
  </svg>
</template>
