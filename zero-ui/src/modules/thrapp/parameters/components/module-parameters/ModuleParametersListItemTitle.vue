<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
</script>

<template>
  <h5 :class="cn('font-ui! text-foreground font-medium', props.class)">
    <slot />
  </h5>
</template>
