<script setup lang="ts">
import { cn } from "@/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{ selected?: boolean; class?: HTMLAttributes["class"] }>();
</script>

<template>
  <li :class="cn(['gap-2 px-6 py-4'], props.class)">
    <slot />
  </li>
</template>

<style lang="scss" scoped>
li {
  @apply flex items-center justify-between border-primary/5 transition-colors disabled:pointer-events-none disabled:opacity-50;

  &.selected {
    @apply font-bold;
  }

  &:not(.selected) {
    @apply font-light;
  }
}
</style>
