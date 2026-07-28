<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
</script>

<template>
  <hgroup :class="cn('bg-background border-border grid gap-3 rounded-md border p-3', props.class)">
    <slot />
  </hgroup>
</template>
