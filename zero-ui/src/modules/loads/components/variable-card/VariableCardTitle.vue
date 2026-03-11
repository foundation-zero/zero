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
        'text-foreground -mt-1 flex max-w-full items-center gap-2.5 pb-1 font-medium capitalize',
        props.class,
      )
    "
  >
    <span
      class="min-h-5 overflow-hidden text-base leading-[1rem]! overflow-ellipsis whitespace-nowrap"
    >
      <slot />
    </span>
  </div>
</template>
