<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{
  class?: HTMLAttributes["class"];
}>();
</script>

<template>
  <span
    data-slot="action"
    :class="cn('text-muted-foreground font-ui text-xs font-normal underline', props.class)"
  >
    <slot />
  </span>
</template>
