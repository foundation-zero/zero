<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{
  class?: HTMLAttributes["class"];
}>();
</script>

<template>
  <header
    :class="
      cn(
        'border-border-subtle flex items-center justify-between border-b pb-2 text-2xl font-semibold',
        props.class,
      )
    "
  >
    <slot />
  </header>
</template>
