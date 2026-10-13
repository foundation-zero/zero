<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = withDefaults(
  defineProps<{ class?: HTMLAttributes["class"]; size?: "sm" | "default" }>(),
  {
    size: "default",
  },
);
</script>

<template>
  <div
    :class="
      cn(
        'flex shrink-0 items-center gap-1',
        { 'w-32 sm:w-49 md:w-32 lg:w-49': props.size === 'default', 'w-12.5': props.size === 'sm' },
        props.class,
      )
    "
  >
    <slot />
  </div>
</template>
