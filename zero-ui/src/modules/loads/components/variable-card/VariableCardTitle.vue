<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{
  class?: HTMLAttributes["class"];
}>();
</script>

<template>
  <div
    :class="
      cn(
        'text-disabled-foreground -mt-2 flex items-center gap-1 pb-2 text-base leading-[1rem]! font-medium text-ellipsis',
        props.class,
      )
    "
  >
    <slot />
  </div>
</template>
