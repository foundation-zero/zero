<script setup lang="ts">
import { cn } from "@/lib/utils";
import type { HTMLAttributes } from "vue";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
</script>

<template>
  <div :class="cn('flex items-center', props.class)">
    <slot name="left">
      <span
        class="flex items-center"
        :class="{ 'w-1/4': $slots.center }"
      >
        <slot name="left-content" />
      </span>
    </slot>
    <span class="grow" />
    <slot name="center" />
    <span class="grow" />
    <slot name="right">
      <span
        class="flex items-center justify-end"
        :class="{ 'w-1/4': $slots.center }"
      >
        <slot name="right-content" />
      </span>
    </slot>
  </div>
</template>
