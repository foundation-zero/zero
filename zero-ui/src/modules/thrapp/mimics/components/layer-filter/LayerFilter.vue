<script setup lang="ts">
import { type Component } from "vue";
import { LayerFilterOption, useLayerFilterContext } from "./layer-filter.provider";

const props = withDefaults(defineProps<{ as?: string | Component; filter: LayerFilterOption }>(), {
  as: "g",
});

const { getFilter } = useLayerFilterContext();
const isActive = getFilter(props.filter);
</script>

<template>
  <component
    :is="as"
    :class="{ 'pointer-events-none opacity-0': !isActive, 'opacity-100': isActive }"
    class="transition-opacity duration-300"
  >
    <slot />
  </component>
</template>
