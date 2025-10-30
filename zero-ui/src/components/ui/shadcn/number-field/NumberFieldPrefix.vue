<script setup lang="ts">
import { cn } from "@/lib/utils";
import type { HTMLAttributes } from "vue";

const props = defineProps<{
  class?: HTMLAttributes["class"];
}>();
</script>

<template>
  <span
    data-slot="prefix"
    :class="
      cn(
        'bg-muted border-border-subtle text-muted-foreground absolute top-0.5 bottom-0.5 left-0.5 flex transform items-center rounded-l-sm border-r px-3 font-mono',
        props.class,
      )
    "
  >
    <slot />
  </span>
</template>
