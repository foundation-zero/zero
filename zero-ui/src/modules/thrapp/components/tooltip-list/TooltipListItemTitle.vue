<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{
  class?: HTMLAttributes["class"];
}>();
</script>

<template>
  <span
    data-slot="title"
    :class="
      cn('flex items-center gap-x-2.5 overflow-hidden font-medium text-ellipsis', props.class)
    "
  >
    <slot />
  </span>
</template>
