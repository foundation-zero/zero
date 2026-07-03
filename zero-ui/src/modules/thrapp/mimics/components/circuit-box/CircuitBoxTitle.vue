<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
</script>

<template>
  <header
    :class="
      cn(
        'text-foreground font-headers flex flex-nowrap items-center font-bold tracking-wider text-nowrap text-ellipsis whitespace-nowrap uppercase',
        props.class,
      )
    "
  >
    <slot />
  </header>
</template>
