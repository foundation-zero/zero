<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
</script>

<template>
  <header
    :class="
      cn(
        'text-foreground font-headers flex items-center font-bold tracking-wider uppercase',
        props.class,
      )
    "
  >
    <slot />
  </header>
</template>
