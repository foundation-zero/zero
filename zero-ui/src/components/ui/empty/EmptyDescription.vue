<script setup lang="ts">
import { cn } from "@common/lib/utils";
import type { HTMLAttributes } from "vue";

const props = defineProps<{
  class?: HTMLAttributes["class"];
}>();
</script>

<template>
  <p
    data-slot="empty-description"
    :class="
      cn(
        'text-muted-foreground [&>a:hover]:text-primary text-sm/relaxed [&>a]:underline [&>a]:underline-offset-4',
        props.class,
      )
    "
  >
    <slot />
  </p>
</template>
