<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";
import { useAutomaticMode } from "../../state";

const props = defineProps<{
  class?: HTMLAttributes["class"];
}>();

const isAutomaticMode = useAutomaticMode();
</script>

<template>
  <span
    data-slot="value"
    :class="
      cn(
        'border-b border-dashed px-2 pb-0.5 whitespace-nowrap',
        { 'border-attention-muted': isAutomaticMode, 'border-warning': !isAutomaticMode },
        props.class,
      )
    "
  >
    <slot />
  </span>
</template>
