<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
</script>

<template>
  <ul
    :class="
      cn('bg-dull border-border grid grow gap-3 border-t border-b py-3 sm:gap-4', props.class)
    "
  >
    <slot />
  </ul>
</template>
