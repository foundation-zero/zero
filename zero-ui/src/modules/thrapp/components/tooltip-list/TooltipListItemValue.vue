<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{
  class?: HTMLAttributes["class"];
}>();
</script>

<template>
  <span
    data-slot="value"
    :class="
      cn('border-attention-muted border-b border-dashed px-2 pb-0.5 whitespace-nowrap', props.class)
    "
  >
    <slot />
  </span>
</template>
