<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
</script>

<template>
  <section
    :class="
      cn(
        'border-border grid gap-4 rounded-2xl border px-4 py-3 sm:grid-cols-2 sm:gap-6 sm:px-6 sm:pb-8 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5',
        props.class,
      )
    "
  >
    <slot />
  </section>
</template>

<style lang="css" scoped>
section {
  background: linear-gradient(
    to bottom,
    color-mix(in oklab, var(--background) 10%, var(--color-muted)),
    color-mix(in oklab, var(--brand) 10%, var(--color-muted)) 100%
  );
}
</style>
