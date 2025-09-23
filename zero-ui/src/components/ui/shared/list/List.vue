<script setup lang="ts">
import { cn } from "@/lib/utils";

defineProps<{ orientation?: "horizontal" | "vertical"; size?: number; class?: string }>();
</script>

<template>
  <ul
    :class="[
      cn(
        'border-primary/10 bg-background grid overflow-hidden rounded-md border hover:cursor-pointer',
        $props.class,
      ),
      { 'divide-y': orientation === 'vertical', 'divide-x': orientation !== 'vertical' },
      `grid-cols-${size ?? 1}`,
    ]"
  >
    <slot />
  </ul>
</template>
