<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import type { HTMLAttributes } from "vue";

const props = defineProps<{
  class?: HTMLAttributes["class"];
}>();
</script>

<template>
  <div
    data-slot="mast-lock-label"
    :class="cn('text-disabled-foreground text-base font-medium', props.class)"
  >
    <slot />
  </div>
</template>
