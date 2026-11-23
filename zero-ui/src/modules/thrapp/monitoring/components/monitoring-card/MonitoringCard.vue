<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import type { HTMLAttributes } from "vue";

/** The box around a timeline, chart or summary. */
const props = defineProps<{ class?: HTMLAttributes["class"] }>();
</script>

<template>
  <section
    :class="
      cn(
        'border-border bg-background flex min-w-0 flex-col gap-3 overflow-hidden rounded-lg border p-4',
        props.class,
      )
    "
  >
    <slot />
  </section>
</template>
