<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
</script>

<template>
  <p :class="cn('text-disabled-foreground text-xs sm:text-sm!', props.class)">
    <slot />
  </p>
</template>
