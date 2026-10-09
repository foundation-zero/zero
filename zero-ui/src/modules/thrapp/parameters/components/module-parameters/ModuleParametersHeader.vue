<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
</script>

<template>
  <header
    :class="
      cn(
        'col-span-full flex justify-between gap-3 text-3xl font-semibold max-sm:flex-col sm:items-center',
        props.class,
      )
    "
  >
    <slot />
  </header>
</template>
