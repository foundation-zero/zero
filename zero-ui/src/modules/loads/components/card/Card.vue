<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
</script>

<template>
  <div
    :class="
      cn(
        'bg-background border-border-subtle flex flex-col items-center justify-end rounded-xs border px-6 py-5',
        props.class,
      )
    "
  >
    <slot />
  </div>
</template>
