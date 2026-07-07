<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{
  class?: HTMLAttributes["class"];
}>();
</script>

<template>
  <span :class="cn('text-foreground text-2xs flex items-center gap-1 font-bold', props.class)">
    <slot />
  </span>
</template>
