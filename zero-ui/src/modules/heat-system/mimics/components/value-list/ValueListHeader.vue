<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
</script>

<template>
  <li
    :class="
      cn('text-muted-foreground text-2xs border-border-subtle flex items-center gap-1', props.class)
    "
  >
    <slot />
  </li>
</template>
