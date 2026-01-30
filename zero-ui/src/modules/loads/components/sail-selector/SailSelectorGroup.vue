<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
</script>

<template>
  <div
    data-slot="sail-selector-group"
    :class="cn('bg-inverse-muted rounded-xl p-4', props.class)"
  >
    <slot />
  </div>
</template>

<style lang="css">
@reference "@/assets/index.css";

[data-slot="sail-selector-position"] {
  &:nth-of-type(n + 2) {
    @apply border-inverse-border-subtle border-t;
  }

  &:last-of-type {
    @apply pb-0;
  }
}
</style>
