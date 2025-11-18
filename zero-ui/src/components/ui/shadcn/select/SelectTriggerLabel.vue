<script setup lang="ts">
import { cn } from "@/lib/utils";
import type { HTMLAttributes } from "vue";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
</script>

<template>
  <label
    data-slot="select-trigger-label"
    :class="
      cn(
        'text-2xs text-disabled-foreground absolute top-0.25 left-3 transition-all duration-150',
        props.class,
      )
    "
  >
    <slot />
  </label>
</template>
